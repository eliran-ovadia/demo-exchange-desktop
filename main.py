import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        
        # self.setLayout(qtw.QVBoxLayout())
        
        # my_label = qtw.QLabel("Hello World")
        # my_label.setFont(qtg.QFont("Helvetica", 20))
        # self.layout().addWidget(my_label)
        
        
        
        form_layout = qtw.QFormLayout()
        self.setLayout(form_layout)
        
        label_1 = qtw.QLabel("Label 1-------------")
        label_1.setFont(qtg.QFont("Helvetica", 20))
        f_name = qtw.QLineEdit(self)
        l_name = qtw.QLineEdit(self)
        form_layout.addRow(label_1)
        form_layout.addRow("First name", f_name)
        form_layout.addRow("Last name", l_name)
        form_layout.addRow(qtw.QPushButton("Submit", clicked = lambda: press()))
        
        
        
        
        # my_text = qtw.QTextEdit(self, lineWrapMode = qtw.QTextEdit.FixedColumnWidth, lineWrapColumnOrWidth = 50, placeholderText = "Enter Text", readOnly = False, acceptRichText = True)
        # self.layout().addWidget(my_text)
        
        
        
        # my_spin = qtw.QSpinBox(self, value = 10, maximum = 100, minimum = 0, singleStep = 20, suffix = " order", prefix = "#")
        # self.layout().addWidget(my_spin)
        # my_spin.setFont(qtg.QFont("Helvetica", 20))
        
        
        # my_combo = qtw.QComboBox(self, editable = True, insertPolicy = qtw.QComboBox.InsertAtTop)
        # my_combo.addItem("Item 1")
        # my_combo.addItem("Item 2")
        # my_combo.addItems(["Item 3", "Item 4", "Item 5"])
        # my_combo.insertItem(0, "Item 0")
        # self.layout().addWidget(my_combo)
        
        
        # my_entry = qtw.QLineEdit()
        # my_entry.setObjectName("name_field")
        # my_entry.setText("Enter Name")
        # self.layout().addWidget(my_entry)
        
        
        # my_button = qtw.QPushButton("Submit", clicked = lambda: press())
        # self.layout().addWidget(my_button)
        # my_button.setFont(qtg.QFont("Helvetica", 20))
        
        def press():
            label_1.setText("Hello " + f_name.text() + " " + l_name.text())
        
        self.show()
        
        
app = qtw.QApplication([])
mw = MainWindow()
app.exec_()