# PDF Reducer

## Overview

PDF Reducer is a web application built using Streamlit that allows users to upload a PDF file and reduce its size by compressing the images within the PDF. The application aims to provide an easy-to-use interface for reducing the file size of PDFs without significantly compromising the quality of the images contained within them.

## Features

- Upload a PDF file for compression.
- Specify a target file size in kilobytes (KB).
- Automatically adjust image compression quality to achieve the target size.
- Download the compressed PDF.

## Installation

To run the PDF Reducer application, you need to have Python installed on your machine. Additionally, you'll need to install the required Python packages. Follow the steps below to set up the environment:

1. Clone the repository or download the source code files.
2. Navigate to the directory containing the source code.
3. Install the required packages using pip:

   ```bash
   pip install streamlit pillow pypdf2
   ```

## Usage

To start the PDF Reducer application, run the following command in your terminal:

```bash
streamlit run app.py
```

This will launch the application in your default web browser.

### User Interface

1. **Upload a PDF file**: Click the "Upload a PDF file" button and select the PDF you want to compress.
2. **Enter target size**: Specify the desired file size in kilobytes (KB) in the "Target size (KB)" input field.
3. **Compress PDF**: The application will process the PDF and compress the images to meet the target file size.
4. **Download Reduced PDF**: Once the compression is complete, a download button will appear, allowing you to download the reduced PDF file.

## Code Explanation

### Imports

```python
from PIL import Image, UnidentifiedImageError
import PyPDF2
import streamlit as st
import io
import os
```

- `PIL` (Python Imaging Library) is used for image processing.
- `PyPDF2` is used for reading and writing PDF files.
- `streamlit` is used to create the web interface.
- `io` and `os` are used for handling file operations.

### Image Compression Function

```python
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
```

- `compress_image` takes an image stream and a quality parameter.
- It opens the image, converts it to RGB, and saves it as a JPEG with the specified quality.
- The compressed image is returned as an in-memory byte stream.

### PDF Compression Function

```python
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
```

- `compress_pdf` reads the input PDF and compresses images within it to achieve the target size.
- It iterates through the PDF pages and compresses images found in the XObject resources.
- The function adjusts the quality parameter to meet the target file size.

### Main Application Function

```python
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
```

- `main` is the entry point of the Streamlit application.
- It provides a user interface for uploading the PDF and specifying the target size.
- It handles the PDF compression and allows the user to download the compressed PDF.

## Contributing

If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them.
4. Push to your fork and submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.