from PIL import Image, UnidentifiedImageError
import PyPDF2
import streamlit as st
import io
import os

def compress_image(image_stream, quality):
    try:
        image = Image.open(image_stream)
        st.write(f"Image format: {image.format}")  # Debugging statement
        image = image.convert('RGB')

        output_io = io.BytesIO()
        image.save(output_io, format='JPEG', quality=quality)
        return output_io
    except UnidentifiedImageError as e:
        return None

def compress_pdf(input_pdf_path, output_pdf_path, target_size_kb):
    target_size_bytes = target_size_kb * 1024
    quality = 50
    step = 5
    max_iterations = 10

    for _ in range(max_iterations):
        input_pdf = PyPDF2.PdfReader(input_pdf_path)
        output_pdf = PyPDF2.PdfWriter()

        for page_number in range(len(input_pdf.pages)):
            page = input_pdf.pages[page_number]

            if '/XObject' in page['/Resources']:
                xObject = page['/Resources']['/XObject'].get_object()

                for obj in xObject:
                    if xObject[obj]['/Subtype'] == '/Image':
                        original_image = xObject[obj].get_data()
                        image_stream = io.BytesIO(original_image)
                        compressed_image_stream = compress_image(image_stream, quality)

                        if compressed_image_stream is not None:
                            xObject[obj]._data = compressed_image_stream.getvalue()

            output_pdf.add_page(page)

        with open(output_pdf_path, 'wb') as output_file:
            output_pdf.write(output_file)

        current_size = os.path.getsize(output_pdf_path)
        if current_size <= target_size_bytes:
            break
        else:
            quality -= step
            if quality <= 10:
                quality = 10  # Minimum quality to avoid excessive degradation

    return current_size

def main():
    st.title("PDF Reducer")

    # File input
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    # Target size input
    target_size_kb = st.text_input("Target size (KB)")

    if uploaded_file and target_size_kb:
        # Convert target size to integer
        try:
            target_size_kb = int(target_size_kb)
        except ValueError:
            st.error("Invalid target size. Please enter a valid number.")
            return

        # Compress PDF
        input_pdf_path = "input.pdf"
        output_pdf_path = "output_reduced.pdf"

        with open(input_pdf_path, "wb") as file:
            file.write(uploaded_file.getvalue())

        compressed_size = compress_pdf(input_pdf_path, output_pdf_path, target_size_kb)

        # Display final file size
        st.success(f"Final file size: {compressed_size / 1024:.2f} KB")
        st.download_button("Download Reduced PDF", data=open(output_pdf_path, "rb").read(), file_name="output_reduced.pdf")

if __name__ == "__main__":
    main()
