# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import datetime
import re
import io
import os
# pyrefly: ignore [missing-import]
import firebase_admin
# pyrefly: ignore [missing-import]
from firebase_admin import credentials, firestore
from pdf_generator import create_wepower_pdf

app = Flask(__name__)
app.secret_key = "wepower_secure_secret_key_change_this"

# --- FIREBASE FIRESTORE INITIALIZATION ---
# Ensure you have placed your 'firebase_credentials.json' file in your project root directory
import os
import json

# Attempt to read credentials from Render's environment variable
firebase_json_str = os.environ.get('FIREBASE_CREDENTIALS')

if firebase_json_str:
    # Running on Render: Convert the JSON string back to a dictionary
    cred_dict = json.loads(firebase_json_str)
    cred = credentials.Certificate(cred_dict)
else:
    # Running locally on your computer: Load the file directly
    cred = credentials.Certificate("firebase_credentials.json")

firebase_admin.initialize_app(cred)
db = firestore.client()
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    return None

def format_pak_cnic(val):
    digits = re.sub(r'\D', '', val)
    digits = digits[:13]
    if len(digits) <= 5:
        return digits
    elif len(digits) <= 12:
        return f"{digits[:5]}-{digits[5:]}"
    else:
        return f"{digits[:5]}-{digits[5:12]}-{digits[12:]}"

def format_pak_phone(val):
    digits = re.sub(r'\D', '', val)
    return digits[:11]

def check_uniqueness(cid, c_cnic, current_user_email, excluding_doc_id=None):
    # Check across Firestore Quotations History
    quotations_ref = db.collection('quotations').stream()
    for doc in quotations_ref:
        rec = doc.to_dict()
        data_obj = rec.get('full_data', rec)
        if data_obj.get('customer_id') == cid:
            return f"Customer ID '{cid}' already exists in system records!"
        if data_obj.get('cnic') == c_cnic:
            return f"CNIC '{c_cnic}' is already registered with another customer!"

    # Check across Firestore Drafts
    drafts_ref = db.collection('drafts').stream()
    for doc in drafts_ref:
        if excluding_doc_id and doc.id == excluding_doc_id:
            continue
        rec = doc.to_dict()
        data_obj = rec.get('full_data', rec)
        if data_obj.get('customer_id') == cid:
            return f"Customer ID '{cid}' already exists in system records!"
        if data_obj.get('cnic') == c_cnic:
            return f"CNIC '{c_cnic}' is already registered with another customer!"
            
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("authenticated"):
        error = None
        if request.method == "POST":
            action = request.form.get("action")
            if action == "login":
                email = request.form.get("email", "").strip().lower()
                password = request.form.get("password", "")
                
                # Fetch user from Firestore 'users' collection
                user_doc = db.collection('users').document(email).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    if user_data.get("password") == password:
                        user_status = user_data.get("status", "active")
                        if str(user_status).lower() == "disabled":
                            error = "Your account has been disabled. Please contact an administrator."
                        else:
                            session["authenticated"] = True
                            session["user_email"] = email
                            session["user_name"] = user_data.get("name")
                            session["user_role"] = user_data.get("role", "sales")
                            return redirect(url_for("index"))
                    else:
                        error = "Invalid Email or Password."
                else:
                    error = "Invalid Email or Password."

        return render_template("index.html", authenticated=False, error=error)

    user_role = session.get("user_role", "sales")

    nav_mode = request.args.get("nav", session.get("nav_mode", "Create New Quotation"))
    if nav_mode == "Manage Users" and user_role != "admin":
        nav_mode = "Create New Quotation"
    session["nav_mode"] = nav_mode
    
    active_draft = session.get("active_draft")
    active_draft_id = session.get("active_draft_id")
    view_quotation_data = session.get("view_quotation_data")
    message = request.args.get("msg")
    error = request.args.get("err")
    new_user_data = None

    current_user_email = session.get("user_email")

    if request.method == "POST":
        form_action = request.form.get("form_action")
        
        if form_action == "logout":
            session.clear()
            return redirect(url_for("index"))

        elif form_action == "create_user":
            if user_role != "admin":
                error = "Unauthorized action!"
            else:
                new_name = request.form.get("new_name", "").strip()
                new_email = request.form.get("new_email", "").strip().lower()
                new_password = request.form.get("new_password", "")
                new_role = request.form.get("new_role", "sales").strip().lower()
                if new_role not in ["admin", "sales"]:
                    new_role = "sales"

                new_user_data = {
                    "new_name": new_name,
                    "new_email": new_email,
                    "new_role": new_role
                }

                email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"

                if not new_name or not new_email or not new_password:
                    error = "Please fill all required user details fields."
                elif not re.match(email_regex, new_email):
                    error = "Please enter a valid email address."
                elif db.collection('users').document(new_email).get().exists:
                    error = "An account with this email already exists!"
                else:
                    pwd_err = validate_password(new_password)
                    if pwd_err:
                        error = pwd_err
                    else:
                        db.collection('users').document(new_email).set({
                            "name": new_name,
                            "email": new_email,
                            "password": new_password,
                            "role": new_role,
                            "status": "active"
                        })
                        return redirect(url_for("index", nav="Manage Users", msg=f"Employee account for {new_name} ({new_role.upper()}) created successfully!"))

        elif form_action == "update_user_password":
            if user_role != "admin":
                error = "Unauthorized action!"
            else:
                target_email = request.form.get("target_email", "").strip().lower()
                new_password = request.form.get("new_password", "")
                pwd_err = validate_password(new_password)
                if pwd_err:
                    error = pwd_err
                else:
                    db.collection('users').document(target_email).update({"password": new_password})
                    return redirect(url_for("index", nav="Manage Users", msg=f"Password for {target_email} updated successfully!"))

        elif form_action in ["save_draft", "publish_quotation"]:
            client_name = request.form.get("client_name", "")
            customer_id = request.form.get("customer_id", "")
            raw_cnic = request.form.get("cnic", "")
            raw_phone = request.form.get("client_phone", "")
            
            cnic = format_pak_cnic(raw_cnic)
            client_phone = format_pak_phone(raw_phone)
            
            system_kw = float(request.form.get("system_kw", 0.0))
            system_type = request.form.get("system_type", "On-Grid System")
            structure_type = request.form.get("structure_type", "Standard")
            inverter_desc = request.form.get("inverter_desc", "")
            inverter_price = float(request.form.get("inverter_price", 0.0))
            has_battery = True if system_type == "Hybrid System" else False
            battery_price = float(request.form.get("battery_price", 0.0)) if has_battery else 0.0
            
            panel_rate = float(request.form.get("panel_rate", 0.0))
            structure_rate = float(request.form.get("structure_rate", 0.0))
            installation_rate = float(request.form.get("installation_rate", 0.0))
            accessories_price = float(request.form.get("accessories_price", 0.0))
            transport_price = float(request.form.get("transport_price", 0.0))
            discount = float(request.form.get("discount", 0.0))
            validity = int(request.form.get("validity", 2))
            payment_terms_text = request.form.get("payment_terms_text", "")

            # Preserve typed form state into active_draft
            typed_payload = {
                "user_email": current_user_email,
                "client_name": client_name.strip(),
                "customer_id": customer_id.strip(),
                "cnic": raw_cnic,
                "client_phone": raw_phone,
                "system_kw": system_kw,
                "system_type": system_type,
                "structure_type": structure_type,
                "inverter_desc": inverter_desc,
                "inverter_price": inverter_price,
                "has_battery": has_battery,
                "battery_price": battery_price,
                "panel_rate": panel_rate,
                "structure_rate": structure_rate,
                "installation_rate": installation_rate,
                "accessories_price": accessories_price,
                "transport_price": transport_price,
                "discount": discount,
                "validity": validity,
                "payment_terms_text": payment_terms_text,
                "Timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            }
            session["active_draft"] = typed_payload
            active_draft = typed_payload

            if not client_name.strip() or not customer_id.strip() or not cnic or not client_phone:
                error = "Required fields missing!"
            elif len(re.sub(r'\D', '', cnic)) != 13:
                error = "Please enter a valid 13-digit Pakistani CNIC number."
            elif len(re.sub(r'\D', '', client_phone)) != 11:
                error = "Please enter a valid 11-digit phone number."
            else:
                conflict = check_uniqueness(customer_id.strip(), cnic, current_user_email, excluding_doc_id=active_draft_id)
                if conflict:
                    error = conflict
                else:
                    if form_action == "save_draft":
                        # If editing an existing draft, update it, else create new
                        if active_draft_id:
                            db.collection('drafts').document(active_draft_id).set(typed_payload)
                        else:
                            new_doc_ref = db.collection('drafts').document()
                            new_doc_ref.set(typed_payload)
                            session["active_draft_id"] = new_doc_ref.id

                        session["active_draft"] = typed_payload
                        return redirect(url_for("index", msg="Quotation successfully saved as Draft!"))

                    elif form_action == "publish_quotation":
                        form_data = {
                            "sales_rep_name": session["user_name"],
                            "sales_rep_email": session["user_email"],
                            "client_name": client_name.strip(),
                            "customer_id": customer_id.strip(),
                            "cnic": cnic,
                            "client_phone": client_phone,
                            "system_type": system_type,
                            "system_kw": system_kw,
                            "structure_type": structure_type,
                            "inverter_desc": inverter_desc if inverter_desc else "N/A",
                            "inverter_price": inverter_price,
                            "has_battery": has_battery,
                            "battery_price": battery_price,
                            "panel_rate": panel_rate,
                            "structure_rate": structure_rate,
                            "installation_rate": installation_rate,
                            "accessories_price": accessories_price,
                            "transport_price": transport_price,
                            "discount": discount,
                            "validity": validity,
                            "payment_terms_text": payment_terms_text,
                            "timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        }
                        
                        pdf_bytes, final_amount = create_wepower_pdf(form_data)
                        
                        history_entry = {
                            "user_email": current_user_email,
                            "Timestamp": form_data["timestamp"],
                            "Sales Rep": session["user_name"],
                            "Client Name": form_data["client_name"],
                            "Customer ID": form_data["customer_id"],
                            "CNIC": cnic,
                            "System": f"{system_kw} kW {system_type.replace(' System', '')}",
                            "Amount (PKR)": f"{final_amount:,}",
                            "full_data": form_data,
                            "pdf_bytes": pdf_bytes
                        }
                        
                        # Save to Firestore quotations collection
                        db.collection('quotations').add(history_entry)
                        
                        # Clean up draft if it was loaded from drafts
                        if active_draft_id:
                            db.collection('drafts').document(active_draft_id).delete()
                            session["active_draft_id"] = None
                        
                        session["active_draft"] = None
                        
                        return redirect(url_for("index", msg=f"Quotation confirmed and published! Total Amount: PKR {final_amount:,}"))

    # Fetch Drafts from Firestore for template display
    drafts_docs = db.collection('drafts').where('user_email', '==', current_user_email).stream()
    drafts_list = []
    for doc in drafts_docs:
        d_data = doc.to_dict()
        d_data['firestore_id'] = doc.id
        drafts_list.append(d_data)

    # Fetch History from Firestore for template display
    history_docs = db.collection('quotations').where('user_email', '==', current_user_email).stream()
    history_list = []
    for doc in history_docs:
        h_data = doc.to_dict()
        h_data['firestore_id'] = doc.id
        history_list.append(h_data)

    # Apply optional search filter from query parameters
    search_term = request.args.get('search')
    field = request.args.get('field')
    if search_term and field:
        term_lower = search_term.strip().lower()
        def matches(item):
            full = item.get('full_data', {})
            if field == 'client_name':
                # stored as 'Client Name' at top level
                val = item.get('Client Name', '') or full.get('client_name', '')
            elif field == 'cnic':
                # stored as 'CNIC' at top level
                val = item.get('CNIC', '') or full.get('cnic', '')
            elif field == 'phone':
                # stored as 'client_phone' inside full_data
                val = full.get('client_phone', '') or item.get('client_phone', '')
            else:
                return False
            return term_lower in str(val).lower()
        history_list = [item for item in history_list if matches(item)]

    # Fetch Users from Firestore if Admin and nav_mode is Manage Users
    users_list = []
    if nav_mode == "Manage Users" and user_role == "admin":
        users_docs = db.collection('users').stream()
        for doc in users_docs:
            u_data = doc.to_dict()
            u_data['firestore_id'] = doc.id
            if 'email' not in u_data or not u_data['email']:
                u_data['email'] = doc.id
            if 'role' not in u_data:
                u_data['role'] = 'sales'
            if 'status' not in u_data:
                u_data['status'] = 'active'
            users_list.append(u_data)

    return render_template(
        "index.html",
        authenticated=True,
        user_name=session.get("user_name"),
        user_email=session.get("user_email"),
        user_role=user_role,
        nav_mode=nav_mode,
        active_draft=active_draft,
        drafts=drafts_list,
        history=history_list,
        users=users_list,
        new_user_data=new_user_data,
        view_data=view_quotation_data,
        msg=message,
        err=error
    )

@app.route("/admin/toggle_user/<string:email>")
def toggle_user(email):
    if not session.get("authenticated") or session.get("user_role") != "admin":
        return redirect(url_for("index", err="Unauthorized access!"))
    
    clean_email = email.strip().lower()
    current_admin_email = str(session.get("user_email", "")).strip().lower()
    
    if clean_email == current_admin_email:
        return redirect(url_for("index", nav="Manage Users", err="You cannot disable your own active admin account!"))
    
    user_ref = db.collection('users').document(clean_email)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        u_data = user_doc.to_dict()
        if str(u_data.get("role", "sales")).lower() == "admin":
            return redirect(url_for("index", nav="Manage Users", err="Admin accounts cannot be revoked or disabled from the portal. They can only be managed directly in the database."))
        current_status = u_data.get("status", "active")
        new_status = "disabled" if str(current_status).lower() == "active" else "active"
        user_ref.update({"status": new_status})
        return redirect(url_for("index", nav="Manage Users", msg=f"Account status for {clean_email} changed to {new_status.upper()}."))
    else:
        return redirect(url_for("index", nav="Manage Users", err="User not found!"))

@app.route("/load_draft/<string:doc_id>")
def load_draft(doc_id):
    doc_ref = db.collection('drafts').document(doc_id).get()
    if doc_ref.exists:
        session["active_draft"] = doc_ref.to_dict()
        session["active_draft_id"] = doc_id
        session["nav_mode"] = "Create New Quotation"
    return redirect(url_for("index", nav="Create New Quotation"))

@app.route("/view_quote/<string:doc_id>")
def view_quote(doc_id):
    doc_ref = db.collection('quotations').document(doc_id).get()
    if doc_ref.exists:
        item = doc_ref.to_dict()
        data = {k: v for k, v in item.items() if k != "pdf_bytes"}
        session["view_quotation_data"] = data
        session["nav_mode"] = "Activity Dashboard"
    return redirect(url_for("index", nav="Activity Dashboard"))

@app.route("/view_pdf/<string:doc_id>")
@app.route("/view_pdf/<string:doc_id>/<string:client_name>.pdf")
def view_pdf(doc_id, client_name=None):
    doc_ref = db.collection('quotations').document(doc_id).get()
    if doc_ref.exists:
        item = doc_ref.to_dict()
        pdf_data = item.get("pdf_bytes")
        if pdf_data:
            if not client_name:
                client_name = item.get("Client Name", "Quotation")
            clean_name = re.sub(r'[^\w\s-]', '', client_name).strip().replace(' ', '_') or "Quotation"
            return send_file(
                io.BytesIO(pdf_data),
                mimetype="application/pdf",
                as_attachment=False,
                download_name=f"{clean_name}.pdf"
            )
    return redirect(url_for("index"))

@app.route("/close_viewer")
def close_viewer():
    session["view_quotation_data"] = None
    return redirect(url_for("index", nav="Activity Dashboard"))

@app.route("/download_pdf/<string:doc_id>")
@app.route("/download_pdf/<string:doc_id>/<string:client_name>.pdf")
def download_pdf(doc_id, client_name=None):
    doc_ref = db.collection('quotations').document(doc_id).get()
    if doc_ref.exists:
        item = doc_ref.to_dict()
        pdf_data = item.get("pdf_bytes")
        if pdf_data:
            if not client_name:
                client_name = item.get("Client Name", "Quotation")
            clean_name = re.sub(r'[^\w\s-]', '', client_name).strip().replace(' ', '_') or "Quotation"
            return send_file(
                io.BytesIO(pdf_data),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"{clean_name}.pdf"
            )
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)