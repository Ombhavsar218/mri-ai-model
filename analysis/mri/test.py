from weasyprint import HTML
HTML(string="<h1>Hello, MRI Report!</h1>").write_pdf("test.pdf")
