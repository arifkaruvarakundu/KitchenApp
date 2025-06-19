# utils/invoice_pdf.py
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

def generate_invoice_pdf(invoice):
    context = {
        "invoice": invoice,
        "order": invoice.order,
        "items": invoice.order.items.all(),
        "customer_name": f"{invoice.order.user.first_name} {invoice.order.user.last_name}",
        "customer_email": invoice.order.user.email,
        "date": invoice.order.created_at.date(),
    }
    html_string = render_to_string("invoice_template.html", context)
    html = HTML(string=html_string)

    result = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    html.write_pdf(result.name)
    return result.name
