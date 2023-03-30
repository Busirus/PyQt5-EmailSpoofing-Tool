<div id="header" align="center">
<h1> PyQt5 Email Spoofing</h1>
</div>



<div id="header" align="center">
   <img src="https://zupimages.net/up/23/13/8dnq.png"/></a>
</div>


# Introduction

This easy-to-use tool allows you to craft emails with a custom sender address and name, while also providing support for HTML templates and attachments. Use it wisely and responsibly.

# DISCLAIMER

This tool is for educational purposes only. Do not use it for any illegal activities. The author is not responsible for any misuse of this tool.

# Installation

1. Clone the repository or download the zip file.

```bash
git clone https://github.com/busirus/PyQt5-EmailSpoofing-Tool.git
```

2. Install the required libraries by running the following command in the terminal:

```bash
pip install -r requirements.txt
```

3. Run the program by executing the following command:

```bash
python main.py 
```

# Features

- Send emails with a spoofed sender address and name
- Supports HTML templates
- Supports adding attachments

# Usage

1. Configure your SMTP settings in config.ini file using your preferred email service provider. For example, i used SendinBlue (free).
2. Enter the destination email, spoofed email, spoofed name, and email subject in the provided fields. If you want to CC an email address, enter it in the CC Email    field.
3. Type or paste the message in the message box, or import an HTML template by clicking the "Import Template" button and selecting a file.
4. If you want to attach files, click the "Attach File" button and select the files you want to attach. To remove attached files, select the file and click the "Remove Attached File" button.
5. Click the "Send Email" button to send the spoofed email with the provided information and attachments.

# License
This project is released under the MIT License. Please refer to the LICENSE file for more information.
