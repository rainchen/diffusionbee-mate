# DiffusionBee Mate

## Overview

**DiffusionBee Mate** is a Python Streamlit application designed to enhance the image review process for users of **DiffusionBee**, a powerful tool for generating images using diffusion models. While **DiffusionBee** excels in installing models and generating images with a user-friendly interface, it lacks convenience for reviewing, comparing, and filtering generated images. **DiffusionBee Mate** bridges this gap by providing an intuitive and customizable platform to manage and analyze your generated images.

## Key Features

- **Grouped by Prompt**: The most significant advantage is that it groups generated images by prompt, enabling quick and straightforward comparisons to determine which diffusion models perform better for specific tasks.
- **Pagination**: List items with pagination, page per size is changeable.
- **Detailed Item Display**: Each history item displays the selected diffusion model, prompt, negative prompt, number of steps, seed, selected style, and generated images.
- **Image Display**: Images are displayed with a fixed maximum width of 200px.
- **Bookmarkable URL**: Allows passing selected page number and page size to the URL.
- **Prompt Parameters as Captions**: Displays some matter prompt parameters as image captions.
- **Search Functionality**: Enables searching by prompt text.
- **Image Deletion**: Allows users to delete images, moving them to the Trash where they can be restored using "Put Back" (Mac OS supported only for now). Automatically backs up the history data file as `~/.diffusionbee/history.json.backup.json` to facilitate restoration.
- **Simplified Maintenance**: The codebase follows the SOLID principles and is designed for easy maintainability.

## Purpose

The primary purpose of **DiffusionBee Mate** is to serve as a helper application for **DiffusionBee** users. While **DiffusionBee** offers a seamless experience for installing models and generating images, it does not provide an efficient way to review, compare, and filter these images. **DiffusionBee Mate** addresses this need by offering a robust set of features tailored for image review and analysis.

## Installation

To run **DiffusionBee Mate** locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/rainchen/diffusionbee-mate.git
   ```

2. Navigate to the project directory:
   ```bash
   cd diffusionbee-mate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

5. Open the WebUI at http://localhost:8501/

## Usage

1. **Loading History Items**: The app loads history from `~/.diffusionbee/history.json` and automatically groups items by prompt
   
   <img width="1822" alt="list-demo-1-fs8" src="https://github.com/user-attachments/assets/c24c68c1-3c3a-4a80-9e77-7733387b8943">



2. **Viewing Details**: Click on an image to view it in full size. Detailed prompt parameters are displayed alongside the image.

   <img width="1822" alt="view-image-params-demo-fs8" src="https://github.com/user-attachments/assets/40033172-aaaf-44de-992b-166a6d93cd0c">




3. **Searching**: Use the search bar in the sidebar to search for specific prompts.

   <img width="1822" alt="sarch-demo-fs8" src="https://github.com/user-attachments/assets/e3dade15-7d94-4995-90f2-56490afb6318">




4. **Deleting Images**: Delete unwanted images. (Notes: Do not delete files while DiffusionBee is running it will overwrite the changes)

    <img width="1822" alt="delete-image-demo-fs8" src="https://github.com/user-attachments/assets/9437815d-c75b-4bbb-8647-44479dcc2aa5">


## Contributing

We welcome contributions to **DiffusionBee Mate**! Please feel free to submit pull requests or open issues for any bugs or feature requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Thank you for using **DiffusionBee Mate**! We hope you find it useful for managing and viewing your diffusion model history items generated by **DiffusionBee**.
