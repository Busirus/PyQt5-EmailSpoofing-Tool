import smtplib
import traceback
import configparser
import os
import lxml.html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit,
                             QMessageBox, QFileDialog, QGridLayout, QListWidget)
from PyQt5 import QtWidgets, QtGui, QtCore
from email.mime.application import MIMEApplication
 

# Read config only once
config = configparser.ConfigParser()
config.read('config.ini')

# Function to send the email
def send_mail(receiver_email, spoofed_email, spoofed_name, message, subject, images, attachments, cc=None):
    try:
        # Create MIMEMultipart message
        msg = MIMEMultipart("related")
        msg['From'] = f"{spoofed_name} <{spoofed_email}>"
        if cc:
            msg['CC'] = cc
        msg['To'] = receiver_email
        msg['Subject'] = subject
        body = message
        msg.attach(MIMEText(body, 'html'))
        # Attach images
        for img_path, img_data in images.items():
            img_part = MIMEImage(img_data)
            img_part.add_header('Content-ID', f'<{img_path}>')
            msg.attach(img_part)
         # Attach files
        for attachment_path in attachments:
            with open(attachment_path, "rb") as attachment_file:
                attachment_part = MIMEApplication(attachment_file.read(), Name=os.path.basename(attachment_path))
                attachment_part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(attachment_part)
        # SMTP configuration
        smtp_host = config.get('SMTP', 'host')
        smtp_port = config.getint('SMTP', 'port')
        smtp_username = config.get('SMTP', 'username')
        smtp_password = config.get('SMTP', 'password')
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(spoofed_email, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        print(traceback.format_exc())
        return False

# Main application class
class EmailSpoofingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.images = {}
        self.attachments = []
        
    # Initialize user interface    
    def init_ui(self):
        layout = QGridLayout()

        label_font = QtGui.QFont()
        label_font.setPointSize(12)
        input_font = QtGui.QFont()
        input_font.setPointSize(11)

   
        self.receiver_email = self.create_line_edit(input_font, "Enter destination email")
        self.cc_email = self.create_line_edit(input_font, "Optional")
        self.spoofed_email = self.create_line_edit(input_font, "Enter email to spoof")
        self.spoofed_name = self.create_line_edit(input_font, "Enter name to spoof")
        self.subject = self.create_line_edit(input_font, "Enter subject")

        self.message = QTextEdit(self)
        self.message.setFont(input_font)
        self.message.setPlaceholderText("Enter message or import .html template")
        self.message.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.message.setMinimumHeight(400)  
        
        message_label = QLabel("Message:")
        message_label.setFont(label_font)
        layout.addWidget(message_label, 0, 2)
        labels = ["Destination Email:", "CC Email:", "Spoofed Email:", "Spoofed Name:", "Subject:"]
        for i, text in enumerate(labels):
            label = QLabel(text)
            label.setFont(label_font)
            layout.addWidget(label, i, 0)
        # Add widgets to layout
        layout.addWidget(self.receiver_email, 0, 1)
        layout.addWidget(self.cc_email, 1, 1)
        layout.addWidget(self.spoofed_email, 2, 1)
        layout.addWidget(self.spoofed_name, 3, 1)
        layout.addWidget(self.subject, 4, 1)
        layout.addWidget(self.message, 1, 2, 5, 1)
        # Add buttons
        button_font = QtGui.QFont()
        button_font.setPointSize(11)
        button_font.setBold(True)
        
        import_button = QPushButton("Import Template", self)
        import_button.setFont(button_font)
        import_button.clicked.connect(self.browse_file)
        layout.addWidget(import_button, 6, 2)
        
        attach_button = QPushButton("Attach File", self)
        attach_button.setFont(button_font)
        attach_button.clicked.connect(self.attach_file)
        layout.addWidget(attach_button, 6, 1)

        remove_button = QPushButton("Remove Attached File", self)
        remove_button.setFont(button_font)
        remove_button.clicked.connect(self.remove_attached_file)
        layout.addWidget(remove_button, 6, 0)

        self.attached_files_list = QListWidget(self)
        self.attached_files_list.setFixedHeight(20)
        layout.addWidget(self.attached_files_list, 7, 0, 1, 2)
        
        send_button = QPushButton("Send Email", self)
        send_button.setFont(button_font)
        send_button.setStyleSheet("background-color: #3A9DCC; color: white;")
        send_button.clicked.connect(self.send_button_clicked)
        layout.addWidget(send_button, 7, 2)

        self.setLayout(layout)

    # Function to create input fields
    def create_line_edit(self, font, placeholder_text):
        line_edit = QLineEdit(self)
        line_edit.setFont(font)
        line_edit.setPlaceholderText(placeholder_text)
        return line_edit

    # Browse file for importing template
    def browse_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select file", "", "HTML Files (*.html *.htm)", options=options)
        if file_path:
            self.import_template(file_path)
            
    # Attach file to email
    def attach_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select file", "", "All Files (*)", options=options)
        if file_path:
            self.attachments.append(file_path)
            item = os.path.basename(file_path)
            self.attached_files_list.addItem(item)
            QMessageBox.information(self, "Success", "File attached successfully.")
            
    # Remove attached file
    def remove_attached_file(self):
        selected_items = self.attached_files_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a file to remove.")
            return
        for item in selected_items:
            row = self.attached_files_list.row(item)
            self.attached_files_list.takeItem(row)
            self.attachments.pop(row)
            QMessageBox.information(self, "Success", "File removed successfully.")

    # Send button click event
    def send_button_clicked(self):
        receiver_email = self.receiver_email.text()
        spoofed_email = self.spoofed_email.text()
        if not receiver_email:
            QMessageBox.critical(self, "Error", "Destination email cannot be empty.")
            return
        if not spoofed_email:
            QMessageBox.critical(self, "Error", "Spoofed email cannot be empty.")
            return
        if send_mail(receiver_email, spoofed_email,
                    self.spoofed_name.text(), self.message.toHtml(), self.subject.text(), self.images, self.attachments, self.cc_email.text()):
            QMessageBox.information(self, "Success", "Email sent successfully.")
        else:
            QMessageBox.critical(self, "Error", "An error occurred while sending the email.")
            
    # Import template function
    def import_template(self, file_path):
        try:
            _, file_ext = os.path.splitext(file_path)
            if file_ext.lower() not in ('.html', '.htm'):
                raise ValueError('Invalid file extension')

            with open(file_path, 'r', encoding='utf-8') as template_file:
                subject_line = template_file.readline().strip()
                if subject_line.startswith('Subject:'):
                    self.subject.setText(subject_line[8:])
                else:
                    self.subject.setText('')

                message_content = template_file.read()

            message_root = lxml.html.fromstring(message_content)
            base_dir = os.path.dirname(file_path)
            self.images = {}
            for img in message_root.xpath('.//img'):
                src = img.attrib.get('src', '')
                img_file_path = os.path.join(base_dir, src)
                if os.path.isfile(img_file_path):
                    with open(img_file_path, 'rb') as img_file:
                        img_data = img_file.read()
                        self.images[src] = img_data
                        self.message.document().addResource(QtGui.QTextDocument.ImageResource, QtCore.QUrl(src), QtGui.QImage.fromData(img_data))
                        message_content = message_content.replace(f'src="{src}"', f'src="{QtCore.QUrl(src).toString()}"')

            self.message.setHtml(message_content)
        except Exception as e:
            QMessageBox.critical(self, "Error", "An error occurred while importing the template.")

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    
    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    
    window = EmailSpoofingApp()
    window.setWindowTitle("Email Spoofing App")
    window.show()
    app.exec_()