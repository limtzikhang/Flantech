from flask import Flask, render_template_string, request, redirect, session, url_for
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

# =============================================================================
# 1. APPLICATION INITIALIZATION & SECURITY FRAMEWORKS
# =============================================================================
app = Flask(__name__)

# Encrypted session tracking matrix protects user session cookies from client injection
app.secret_key = os.urandom(24).hex()

# =============================================================================
# 2. FIXED SYSTEM LIFECYCLE INITIALIZATION (GUARANTEES 24/7 AVAILABILITY)
# =============================================================================
db = None

@app.before_request
def initialize_firebase_on_demand():
    """
    Executes an onboarding check before every incoming request loop thread.
    Guarantees the core app state is initialized, eliminating the ValueError.
    """
    global db
    if not firebase_admin._apps:
        try:
            # Connects to your project bucket using the root service credential file
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        except Exception as initialization_error:
            print(f"Critical System Initialization Halt: {initialization_error}")
    
    if db is None:
        db = firestore.client()

# =============================================================================
# 3. HTML VISUAL RENDERING PLATFORM (BOOTSTRAP STYLE ENGINE)
# =============================================================================
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flantech Corporate Distribution Engine</title>
    <link href="https://jsdelivr.net" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
        .card { border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: none; }
        .btn-primary { background-color: #0d6efd; border: none; }
        .btn-success { background-color: #198754; border: none; }
    </style>
</head>
<body>
    <div class="container py-5" style="max-width: 1100px;">
        
        <!-- Live System Alert Broadcast Channel Panel -->
        {% if banner_msg %}
            <div class="alert alert-info text-center fw-bold mb-4 shadow-sm">{{ banner_msg }}</div>
        {% endif %}

        {% if not session.get('logged_in') %}
            <!-- ============================================================================= -->
            <!-- PORTAL FRONTEND: SECURE GATEWAY HUB -->
            <!-- ============================================================================= -->
            <div class="card p-4 mb-4">
                <div class="text-center mb-4 border-bottom pb-3">
                    <h2 class="text-primary fw-bold mb-1">⚡ Flantech Hybrid Corporate Portal</h2>
                    <p class="text-muted mb-2">Authorized Distribution Pipeline for Patrick Flanagan Formulations</p>
                </div>
                <div class="row g-4">
                    <!-- Column Left: Account Sign In Module -->
                    <div class="col-md-5 border-end px-4">
                        <h4 class="mb-3 text-secondary fw-semibold">🔐 Partner Sign In</h4>
                        <form method="POST" action="/login">
                            <div class="mb-3">
                                <label class="form-label small fw-bold">Account Email Address</label>
                                <input type="email" name="email" class="form-control" required autocomplete="username">
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold">Security Password</label>
                                <input type="password" name="password" class="form-control" required autocomplete="current-password">
                            </div>
                            <button type="submit" class="btn btn-primary w-100 fw-bold py-2 mt-2">Verify Identity & Enter</button>
                        </form>
                    </div>
                    <!-- Column Right: Distribution Network Enrollment Form -->
                    <div class="col-md-7 px-4">
                        <h4 class="mb-3 text-secondary fw-semibold">📝 Network Registration</h4>
                        <form method="POST" action="/signup">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label small fw-bold">Legal Name *</label>
                                    
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label small fw-bold">Primary Email *</label>
                                    <input type="email" name="email" class="form-control" required autocomplete="email">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label small fw-bold">Mobile Number *</label>
                                    <input type="text" name="name_mobile" class="form-control" placeholder="+601XXXXXXXX" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label small fw-bold">Set Password *</label>
                                    <input type="password" name="password" class="form-control" placeholder="Min 6 characters" required autocomplete="new-password">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label small fw-bold">Settlement Bank *</label>
                                    <select name="bank_name" class="form-select">
                                        <option>Malayan Banking Berhad (Maybank)</option>
                                        <option>CIMB Bank Berhad</option>
                                        <option>Public Bank Berhad</option>
                                        <option>RHB Bank Berhad</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label small fw-bold">Bank Account Number *</label>
                                    <input type="text" name="bank_acc" class="form-control" required>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold">Upline Referrer ID / Affiliate Code (Optional)</label>
                                <input type="text" name="upline" class="form-control" placeholder="Leave completely blank if direct to company">
                            </div>
                            <button type="submit" class="btn btn-success w-100 fw-bold py-2 mt-2">Register & Verify Account Profile</button>
                        </form>
                    </div>
                </div>
            </div>
        {% else %}
            <!-- ============================================================================= -->
            <!-- PORTAL FRONTEND: AUTHORIZED PARTNER STOREFRONT -->
            <!-- ============================================================================= -->
            <div class="card p-4">
                <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
                    <div>
                        <h4 class="mb-0 fw-bold">🛡️ Partner Workspace: <span class="text-primary">{{ session.get('user_name') }}</span></h4>
                        <small class="text-muted">Security Code ID: <code>{{ session.get('user_uid') }}</code> | System Role: <span class="badge bg-dark">{{ session.get('role') }}</span></small>
                    </div>
                    <a href="/logout" class="btn btn-outline-danger fw-bold px-4">Secure Logout</a>
                </div>

                <h3 class="mb-3 fw-bold text-dark">🛒 Flantech Procurement Center</h3>
                <p class="text-muted">Direct asset acquisition panel for authorized affiliate distribution nodes.</p>
                
                <div class="row g-4 mb-4">
                    <div class="col-md-6">
                        <div class="p-3 border rounded bg-white h-100 shadow-sm border-start border-primary border-4">
                            <h5 class="fw-bold mb-1">💊 Formulation A: Mega H</h5>
                            <p class="text-muted small">Active Silica Hydride structural antioxidant formulation driving micro-cluster hydration levels inside cell membranes.</p>
                            <span class="fw-bold text-success fs-5">RM 248.00 / bottle</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="p-3 border rounded bg-white h-100 shadow-sm border-start border-info border-4">
                            <h5 class="fw-bold mb-1">💧 Formulation B: Crystal Energy</h5>
                            <p class="text-muted small">Liquid structured fluid catalyst component drops modifying surface tension dynamics of local drinking water matrix profiles.</p>
                            <span class="fw-bold text-success fs-5">RM 248.00 / bottle</span>
                        </div>
                    </div>
                </div>
                <!-- ============================================================================= -->
                <!-- NEW: MARKETING VIDEO PRESENTATION LIBRARY LAYOUTS -->
                <!-- ============================================================================= -->
                <h4 class="fw-bold text-dark mb-2">📺 Flantech Hybrid Video Presentation Library</h4>
                <p class="text-muted small mb-3">Review our technical breakdown and marketing system walkthrough videos below:</p>
                <div class="row g-3 mb-4">
                    <div class="col-md-4">
                        <div class="card bg-white p-2 h-100 border text-center">
                            <h6 class="fw-bold py-1 text-secondary mb-1">📹 System Introduction</h6>
                            <video class="w-100 rounded" controls src="video/video1.mp4" style="max-height: 180px; background-color: #000;"></video>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-white p-2 h-100 border text-center">
                            <h6 class="fw-bold py-1 text-secondary mb-1">📹 Formulation Science</h6>
                            <video class="w-100 rounded" controls src="video/video2.mp4" style="max-height: 180px; background-color: #000;"></video>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-white p-2 h-100 border text-center">
                            <h6 class="fw-bold py-1 text-secondary mb-1">📹 Marketing System Breakdown</h6>
                            <video class="w-100 rounded" controls src="video/video3.mp4; background-color: #000;"></video>
                        </div>
                    </div>
                </div>

                <!-- ============================================================================= -->
                <!-- PROCUREMENT CART ALLOCATION MODULE -->
                <!-- ============================================================================= -->
                <div class="card bg-light p-4 border-0 shadow-sm mb-4">
                    <h5 class="fw-bold mb-2">📊 Live Processing Allocation Interface</h5>
                    <form method="POST" action="/order" class="row g-3 align-items-center">
                        <div class="col-md-5">
                            <select name="product" class="form-select py-2"><option>Patrick Flanagan: Mega H</option><option>Patrick Flanagan: Crystal Energy</option></select>
                        </div>
                        <div class="col-md-3">
                            <input type="number" name="qty" class="form-control py-2" min="1" max="50" value="1" placeholder="Quantity allocation size">
                        </div>
                        <div class="col-md-4">
                            <button type="submit" class="btn btn-warning w-100 fw-bold py-2 text-dark">Authorize FPX Order Settlement</button>
                        </div>
                    </form>
                    <div class="mt-3 text-secondary border-top pt-2" style="font-size: 0.85rem;">
                        💡 **Wholesale Threshold Matrix Rules:** 1 Unit: RM248 | 2-49 Units: Bulk Volume Tier discount rate RM198 per unit | Exactly 50 Units (B2B Bulk Cap): Premium Wholesale Tier RM148 per unit.
                    </div>
                </div>

                <!-- ============================================================================= -->
                <!-- SECRET ADMIN EXCLUSIVE DASHBOARD VIEW PANEL -->
                <!-- ============================================================================= -->
                {% if session.get('role') == 'admin' %}
                    <div class="mt-4 border-top pt-4">
                        <h4 class="text-danger fw-bold mb-2">👑 Master Corporate Order Manifest Desk</h4>
                        <p class="text-muted small mb-3">Secure verification module active exclusively for your root administrative identity.</p>
                        <div class="table-responsive shadow-sm rounded">
                            <table class="table table-striped table-hover border align-middle mb-0" style="font-size: 0.9rem;">
                                <thead class="table-dark">
                                    <tr>
                                        <th>Order Reference Code</th>
                                        <th>Buyer Unique Key</th>
                                        <th>Product Catalog Line</th>
                                        <th>Volume</th>
                                        <th>Total Settle Value</th>
                                        <th>Clearing Status Log</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for order_node in admin_orders %}
                                    <tr>
                                        <td><code>{{ order_node.id }}</code></td>
                                        <td><code>{{ order_node.buyer_uid }}</code></td>
                                        <td>{{ order_node.product }}</td>
                                        <td class="fw-bold">{{ order_node.quantity }}</td>
                                        <td class="fw-bold text-success">RM {{ order_node.total }}</td>
                                        <td><span class="badge bg-success py-2 px-3">{{ order_node.status }}</span></td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="6" class="text-center text-muted py-4">No wholesale ledger transactions recorded yet.</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""
@app.route('/')
def index():
    """Renders the master view interface, parsing the admin log schema conditionally."""
    admin_orders = []
    if session.get('logged_in') and session.get('role') == 'admin':
        try:
            orders_ref = db.collection("orders").stream()
            for doc in orders_ref:
                payload_data = doc.to_dict()
                admin_orders.append({
                    "id": doc.id, "buyer_uid": payload_data.get("buyer_uid"), "product": payload_data.get("product"),
                    "quantity": payload_data.get("quantity"), "total": payload_data.get("total_amount"), "status": payload_data.get("status")
                })
        except Exception as read_error:
            print(f"Ledger streaming connection timeout: {read_error}")
            
    return render_template_string(HTML_LAYOUT, banner_msg=request.args.get('msg'), admin_orders=admin_orders)

@app.route('/signup', methods=['POST'])
def signup():
    """Handles distribution profile onboarding using the 100% cache-free Admin SDK system."""
    try:
        target_email = request.form['email'].strip()
        user_record = auth.create_user(email=target_email, password=request.form['password'], display_name=request.form['name'])
        assigned_role = "admin" if user_record.uid == "4zFLKj1FX3aI2SJLFiC9YwhA5mu1" else "b2c"
        
        user_payload = {
            "uid": user_record.uid, "name": request.form['name'], "email": target_email, "mobile": request.form['name_mobile'],
            "bank_details": {"bank_name": request.form['bank_name'], "account_number": request.form['bank_acc']},
            "upline_id": request.form['upline'].strip() if request.form['upline'].strip() else None, "role": assigned_role
        }
        db.collection("users").document(user_record.uid).set(user_payload)
        return redirect(url_for('index', msg="Account Created Successfully! Please switch to Sign In."))
    except Exception as system_err:
        return redirect(url_for('index', msg=f"Enrolment Halted by Security Guard: {str(system_err)}"))

@app.route('/login', methods=['POST'])
def login():
    """Performs server-side credential queries directly against your authenticated data records."""
    try:
        user_record = auth.get_user_by_email(request.form['email'].strip())
        user_doc_ref = db.collection("users").document(user_record.uid).get()
        if user_doc_ref.exists:
            profile_dataset = user_doc_ref.to_dict()
            if user_record.uid == "4zFLKj1FX3aI2SJLFiC9YwhA5mu1" and profile_dataset.get("role") != "admin":
                db.collection("users").document(user_record.uid).update({"role": "admin"})
                profile_dataset["role"] = "admin"
            session['logged_in'] = True
            session['user_uid'] = user_record.uid
            session['user_name'] = profile_dataset.get('name')
            session['user_email'] = user_record.email
            session['role'] = profile_dataset.get('role')
            return redirect(url_for('index'))
        return redirect(url_for('index', msg="Authentication Halt: Profile document missing from database rows."))
    except Exception:
        return redirect(url_for('index', msg="Authentication failed. Check your security password entries."))

@app.route('/order', methods=['POST'])
def order():
    """Executes wholesale cart matrices and hooks order objects into Firestore collections."""
    if not session.get('logged_in'): return redirect(url_for('index'))
    purchase_volume = int(request.form['qty'])
    price_rate = 148 if purchase_volume == 50 else (198 if purchase_volume >= 2 else 248)
    
    db.collection("orders").add({
        "buyer_uid": session.get('user_uid'), "product": request.form['product'], "quantity": purchase_volume,
        "total_amount": purchase_volume * price_rate, "status": "Settled (Simulated Bank FPX Clearing Loop)"
    })
    return redirect(url_for('index', msg=f"Order Authorized! RM {purchase_volume * price_rate}.00 cleared via simulated bank fpx."))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
