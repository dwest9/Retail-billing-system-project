"""Contains the functionality for finalizing orders"""
import datetime
from pathlib import Path
import re
from tkinter import (
    Button,
    Entry,
    Label,
    OptionMenu,
    StringVar,
    Toplevel,
    messagebox,
)
import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app import App


class FinalizeOrderView(Toplevel):
    """Finalize order GUI window"""

    def __init__(self, app: App, order_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.order_id = order_id
        self.geometry("300x300")
        Label(self, text="Customer Information").grid(row=0, column=0, columnspan=2)

        Label(self, text="Name:").grid(row=1, column=0)
        self.name_entry = Entry(self, width=20)
        self.name_entry.grid(row=1, column=1)

        Label(self, text="Phone Number:").grid(row=2, column=0)
        self.phone_entry = Entry(self, width=20)
        self.phone_entry.grid(row=2, column=1)

        Label(self, text="Email:").grid(row=3, column=0)
        self.email = StringVar()
        self.email_entry = Entry(self, width=20, textvariable=self.email)
        self.email_entry.grid(row=3, column=1)

        all_payment_types = self.app.get_all_payment_types()
        self.payment_types = {name: id for id, name in all_payment_types}
        self.result = StringVar(value=all_payment_types[0][1])
        self.payment = OptionMenu(self, self.result, *self.payment_types.keys())
        self.payment.grid(row=4, column=0, columnspan=2)

        Button(self, text="Print", command=self.handle_print_bill).grid(row=5, column=0)
        Button(self, text="Email", command=self.handle_email_bill).grid(row=5, column=1)
        Button(self, text="Print and email", command=self.handle_print_and_email).grid(
            row=5, column=2
        )
        Button(self, text="No Receipt", command=self.handle_no_receipt).grid(
            row=6, column=1
        )

    def handle_print_and_email(self):
        """Handles the print and email button"""
        self.close_order()
        self.print_bill_content()
        self.send_email()
        self.event_generate("<<Finalized>>")
        self.destroy()

    def handle_print_bill(self):
        """Handles the print button"""
        self.close_order()
        self.print_bill_content()
        self.event_generate("<<Finalized>>")
        self.destroy()

    def handle_email_bill(self):
        """Handles the email button"""
        self.close_order()
        self.send_email()
        self.event_generate("<<Finalized>>")
        self.destroy()

    def handle_no_receipt(self):
        """Handles the no receipt button"""
        self.close_order()
        self.event_generate("<<Finalized>>")
        self.destroy()

    def close_order(self):
        """Handles closing the order"""
        if self.name_entry.get() != "":
            customer_id = self.app.order_system.create_customer(
                self.name_entry.get(), self.phone_entry.get(), self.email_entry.get()
            )
            self.app.order_system.add_customer_to_order(self.order_id, customer_id)

        self.app.order_system.pay_for_order(
            self.order_id, self.payment_types[self.result.get()]
        )

    def send_email(self):
        """Handles sending the bill as an email"""

        order_details = self.app.order_system.get_order_details(self.order_id)
        bill_content = order_details.to_string().replace("\n", "<br />")

        # Validating the email address before sending email to the customer
        if not self.email_validator(self.email.get()):
            # Handle the validation error
            messagebox.showerror(
                "Invalid email address",
                "Email address is invalid. Please enter a valid email address.",
            )
            return

        message = Mail(
            from_email="zrp594@usask.ca",
            to_emails=self.email.get(),
            subject="Order Receipt",
            html_content=f"<strong>{bill_content}</strong>",
        )

        try:
            sendgrid = SendGridAPIClient(
                "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"
            )
            response = sendgrid.send(message)
            if response.status_code != 202:
                print(response.status_code)
                print(response.headers)
                print(response.body)
                messagebox.showerror(
                    "Error sending email",
                    "Sendgrid responded with an error while attempting to send email",
                )
            else:
                messagebox.showinfo("Bill Sent Successfully", "Bill Sent Successfully")
        except requests.exceptions.RequestException as network_error:
            # Handle network errors while attempting to send the email
            error_message = f" Network error while sending email: {str(network_error)} "
            messagebox.showerror("Failed to send email", error_message)

    def email_validator(self, email: str) -> bool:
        """Checks if a given email address is valid

        Args:
            email (str): email address to validate

        Returns:
            bool: true is the email is valid, otherwise false
        """
        # Email validation using a regular expression according to RFC 5322 standard.
        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        return re.match(email_regex, email) is not None

    def print_bill_content(self):
        """Handles printing the bill contents"""

        order_details = self.app.order_system.get_order_details(self.order_id)
        bill_content = order_details.to_string()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        # Ensure the bills directory exists
        Path("bills").mkdir(parents=True, exist_ok=True)

        path = Path("bills", f"bill-{timestamp}-{self.order_id}.txt")

        # this is to read and print file
        with open(path, "w", encoding="utf-8") as file:
            file.write(bill_content)
        os.startfile(path, "print")
