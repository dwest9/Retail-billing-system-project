from tkinter import Button, Entry, Label, OptionMenu, StringVar, Toplevel, messagebox

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


from app import App


class FinalizeOrderView(Toplevel):
    def __init__(self, app: App, dashboard, order_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.order_id = order_id
        self.dashboard = dashboard
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
        Button(self, text="No Receipt", command=self.close_order).grid(row=6, column=1)

    def handle_print_and_email(self):
        """Handles the print and email button"""
        self.close_order()
        self.print_bill_content()
        self.send_email()
        self.dashboard.deiconify()
        self.destroy()

    def handle_print_bill(self):
        """Handles the print button"""
        self.close_order()
        self.print_bill_content()
        self.dashboard.deiconify()
        self.destroy()

    def handle_email_bill(self):
        """Handles the email button"""
        self.close_order()
        self.send_email()
        self.dashboard.deiconify()
        self.destroy()

    def handle_no_receipt(self):
        """Handles the no receipt button"""
        self.close_order()
        self.dashboard.deiconify()
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
        print(self.app.order_system.get_order_details(self.order_id))

    def send_email(self):
        """Handles sending the bill as an email"""
        # using SendGrid's Python Library
        # https://github.com/sendgrid/sendgrid-python

        order_details = self.app.order_system.get_order_details(self.order_id)
        bill_content = order_details.to_string().replace("\n", "<br />")
        message = Mail(
            from_email="zrp594@usask.ca",
            to_emails=self.email.get(),
            subject="Order Reciept",
            html_content=f"<strong>{bill_content}</strong>",
        )
        try:
            sg = SendGridAPIClient(
                "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"
            )
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
            messagebox.showinfo("Bill Send Successfully", "Bill Sent Successfully")
        except Exception as e:
            messagebox.showerror("Failed to send email", "Error while sending email")
            print(e)

    def print_bill_content(self):
        """Handles printing the bill contents"""
        order_details = self.app.order_system.get_order_details(self.order_id)
        bill_content = order_details.to_string()

        # this is to read and print file
        file = open(f"bill-{self.order_id}.txt", "w", encoding="utf-8")
        file.write(bill_content)
        file.close()
        os.startfile(f"bill-{self.order_id}.txt", "print")
