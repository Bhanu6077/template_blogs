from flask import Flask, request, send_file, render_template
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
import base64
import uuid
import os

app = Flask(__name__)

# create temp folder for images
if not os.path.exists("temp"):
    os.makedirs("temp")


# convert base64 image → file
def save_base64_image(data):
    header, encoded = data.split(",", 1)
    filename = f"temp/{uuid.uuid4()}.jpg"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(encoded))
    return filename


# home page
@app.route('/')
def home():
    return render_template('index.html')


# -------- PDF EXPORT --------
@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    doc = SimpleDocTemplate("blog.pdf")
    styles = getSampleStyleSheet()
    elements = []

    # main fields
    title = request.form.get("title")
    desc = request.form.get("description")
    hero = request.files.get("hero")

    if hero:
        path = f"temp/{hero.filename}"
        hero.save(path)
        elements.append(Image(path, width=500, height=250))
        elements.append(Spacer(1, 20))

    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph(desc, styles['Normal']))
    elements.append(Spacer(1, 15))

    # sections loop
    i = 0
    while True:
        heading = request.form.get(f"heading_{i}")
        content = request.form.get(f"content_{i}")
        image = request.files.get(f"image_{i}")

        if not heading and not content:
            break

        elements.append(Paragraph(heading, styles['Heading2']))
        elements.append(Paragraph(content, styles['Normal']))

        if image:
            path = f"temp/{image.filename}"
            image.save(path)
            elements.append(Image(path, width=400, height=250))

        elements.append(Spacer(1, 15))
        i += 1

    doc.build(elements)
    return send_file("blog.pdf", as_attachment=True)

@app.route('/export-docx', methods=['POST'])
def export_docx():
    from docx import Document

    doc = Document()

    title = request.form.get("title")
    desc = request.form.get("description")
    hero = request.files.get("hero")

    doc.add_heading(title, 0)
    doc.add_paragraph(desc)

    if hero:
        path = f"temp/{hero.filename}"
        hero.save(path)
        doc.add_picture(path)

    i = 0
    while True:
        heading = request.form.get(f"heading_{i}")
        content = request.form.get(f"content_{i}")
        image = request.files.get(f"image_{i}")

        if not heading and not content:
            break

        doc.add_heading(heading, level=1)
        doc.add_paragraph(content)

        if image:
            path = f"temp/{image.filename}"
            image.save(path)
            doc.add_picture(path)

        i += 1

    doc.save("blog.docx")
    return send_file("blog.docx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)