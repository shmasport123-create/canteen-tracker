import os
from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import database as db

load_dotenv()
db.init_db()

app = Flask(__name__)
OWNER_PHONE = os.getenv("OWNER_PHONE")

def normalize(phone):
    phone = phone.strip().replace("-", "").replace(" ", "")
    if not phone.startswith("+"):
        phone = "+972" + phone.lstrip("0")
    return phone

@app.route("/sms", methods=["POST"])
def sms_webhook():
    from_number = request.form.get("From", "").strip()
    body = request.form.get("Body", "").strip()
    parts = body.split()
    command = parts[0].upper() if parts else ""
    resp = MessagingResponse()

    if from_number == OWNER_PHONE:
        if command == "ADD" and len(parts) >= 3:
            phone = normalize(parts[1])
            name = " ".join(parts[2:])
            success = db.add_member(phone, name)
            resp.message(f"Added {name}!" if success else f"{phone} already exists.")

        elif command == "BAL" and len(parts) == 2:
            phone = normalize(parts[1])
            member = db.get_member(phone)
            if member:
                resp.message(f"{member[2]} owes: {member[3]:.2f}")
            else:
                resp.message("Friend not found. Use ADD first.")

        elif command == "PAID" and len(parts) == 3:
            phone = normalize(parts[1])
            try:
                amount = float(parts[2])
                member = db.get_member(phone)
                if member:
                    db.add_payment(phone, amount)
                    resp.message(f"Payment of {amount:.2f} recorded for {member[2]}.")
                else:
                    resp.message("Friend not found.")
            except ValueError:
                resp.message("Usage: PAID [phone] [amount]")

        elif command == "LIST":
            members = db.get_all_members()
            if members:
                lines = ["Balances:"]
                for m in members:
                    lines.append(f"{m[2]}: {m[3]:.2f}")
                resp.message("\n".join(lines))
            else:
                resp.message("No members yet.")
        else:
            resp.message("Commands: ADD [phone] [name] | BAL [phone] | PAID [phone] [amount] | LIST")
    else:
        member = db.get_member(from_number)
        if not member:
            resp.message("You are not registered. Contact the owner.")
        elif command == "TAKE" and len(parts) >= 3:
            try:
                amount = float(parts[-1])
                item = " ".join(parts[1:-1])
                db.add_take(from_number, item, amount)
                new_bal = member[3] + amount
                resp.message(f"Recorded: {item} - {amount:.2f}\nYour total: {new_bal:.2f}")
            except ValueError:
                resp.message("Usage: TAKE [item] [price]  Example: TAKE Coke 5")
        elif command == "BAL":
            resp.message(f"Your balance: {member[3]:.2f}")
        else:
            resp.message("Commands: TAKE [item] [price] | BAL")

    return str(resp)

@app.route("/")
def portal():
    members = db.get_all_members()
    transactions = db.get_transactions()
    return render_template("portal.html", members=members, transactions=transactions)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
