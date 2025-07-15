import sys
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTableWidgetItem, QMessageBox,
                             QHeaderView, QPushButton, QVBoxLayout, QWidget, QTableWidget, QDateEdit, QTextEdit, QLabel, QGroupBox, QHBoxLayout)
from PyQt5.QtCore import pyqtSlot, QRect, Qt, QDate

# --- Matplotlib Imports ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from budgetPalmain_ui import Ui_MainWindow
import database as db



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- Load Polished Stylesheet ---
        try:
            with open("styles.qss", "r") as style_file:
                self.setStyleSheet(style_file.read())
        except FileNotFoundError:
            # This warning is harmless, but reminds you to keep styles.qss in the same folder
            print("Warning: styles.qss not found. Running with default styles.")

        # --- Database Setup ---
        self.conn = db.create_connection()
        db.create_all_tables(self.conn)

        # --- Initial UI State ---
        self.ui.icons_only_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.dashboard_btn2.setChecked(True)

        # --- Page-Specific Setups ---
        self.setup_dashboard()
        self.setup_expense_page()
        self.setup_income_page()
        self.setup_budget_page()
        self.setup_reports_page()
        self.setup_settings_page()

        # --- Connect Signals to Slots ---
        self.ui.expenseAddButton.clicked.connect(self.add_expense)
        self.ui.pushButton.clicked.connect(self.add_income)
        self.ui.addbudgetbtn.clicked.connect(self.add_budget)
        self.ui.addgoalbtn.clicked.connect(self.add_saving_goal)
        self.ui.pushButton_4.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(6))
        
        # --- Add Tooltips for better UX ---
        self.ui.exit_btn1.setToolTip("Exit Application")
        self.ui.exit_btn2.setToolTip("Exit Application")

        # --- Load all data on startup ---
        self.refresh_all_data()

    def setup_dashboard(self):
        # --- Graph Setup ---
        self.graph_container = QWidget(self.ui.frame_2)
        self.graph_container.setGeometry(QRect(40, 70, 530, 210))
        self.ui.label_58.hide()
        self.ui.label_59.hide()
        layout = QVBoxLayout(self.graph_container)
        layout.setContentsMargins(0, 0, 0, 0)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # --- Overview Setup (Replaces cluttered text) ---
        labels_to_hide = [self.ui.label_60, self.ui.label_61, self.ui.label_62, self.ui.label_63, self.ui.label_64, self.ui.label_65,
                          self.ui.label_66, self.ui.label_67, self.ui.label_68, self.ui.label_69, self.ui.label_70, self.ui.label_71]
        for label in labels_to_hide:
            label.hide()
        
        self.overview_text = QTextEdit(self.ui.frame_2)
        self.overview_text.setGeometry(QRect(40, 310, 530, 100))
        self.overview_text.setReadOnly(True)
        
    def setup_expense_page(self):
        self.ui.label_13.hide()
        # Create a container widget for the graph within frame_10
        # Dynamically set height based on expected number of items or provide more vertical space
        # Adjusted size to prevent cutting. Original was 0,0,371,221
        self.expense_graph_container = QWidget(self.ui.frame_10)
        # Giving more vertical space and also adjusting horizontal to prevent cutoff for labels.
        self.expense_graph_container.setGeometry(QRect(10, 10, 290, 220))
        
        # Create a layout for the graph container
        layout = QVBoxLayout(self.expense_graph_container)
        layout.setContentsMargins(0, 0, 0, 0) #
        
        # Create the Matplotlib figure and canvas
        self.expense_figure = plt.figure()
        self.expense_canvas = FigureCanvas(self.expense_figure)
        layout.addWidget(self.expense_canvas)

        self.ui.dateTimeEdit.setCalendarPopup(True)
        self.ui.dateTimeEdit.setDisplayFormat("yyyy-MM-dd")

    def setup_income_page(self):
        self.ui.label_77.hide()
        self.ui.textBrowser_6.hide()
        self.ui.textBrowser_7.hide()
        self.ui.textBrowser_8.hide()
        self.ui.label_78.hide()
        self.ui.label_79.hide()
        self.ui.label_80.hide()
        self.income_history_table = QTableWidget(self.ui.frame_3)
        self.income_history_table.setGeometry(QRect(240, 310, 380, 191))
        self.income_history_table.setColumnCount(4)
        self.income_history_table.setHorizontalHeaderLabels(["Date", "Source", "Amount", "Notes"])
        self.ui.lineEdit_6.hide()
        self.income_date_picker = QDateEdit(self.ui.frame_3)
        self.income_date_picker.setGeometry(self.ui.lineEdit_6.geometry())
        self.income_date_picker.setCalendarPopup(True)
        self.income_date_picker.setDate(QDate.currentDate())
        self.income_date_picker.setDisplayFormat("yyyy-MM-dd")
        
    def setup_budget_page(self):
        self.ui.dateTimeEdit_2.setCalendarPopup(True)
        self.ui.dateTimeEdit_2.setDisplayFormat("yyyy-MM-dd")

    def setup_reports_page(self):
        self.ui.frame_158.hide()
        self.ui.frame_160.hide()
        self.ui.frame_178.hide()
        self.ui.frame_180.hide()
        self.bar_chart_container = QWidget(self.ui.frame_7)
        self.bar_chart_container.setGeometry(QRect(30, 80, 280, 400))
        bar_layout = QVBoxLayout(self.bar_chart_container)
        self.bar_figure = plt.figure()
        self.bar_canvas = FigureCanvas(self.bar_figure)
        bar_layout.addWidget(self.bar_canvas)
        self.pie_chart_container = QWidget(self.ui.frame_7)
        self.pie_chart_container.setGeometry(QRect(320, 80, 280, 400))
        pie_layout = QVBoxLayout(self.pie_chart_container)
        self.pie_figure = plt.figure()
        self.pie_canvas = FigureCanvas(self.pie_figure)
        pie_layout.addWidget(self.pie_canvas)
        
    def setup_settings_page(self):
        
        # Hide original elements that will be replaced or are not needed
        self.ui.radioButton.hide()
        self.ui.tabWidget.hide()
        self.ui.label_24.hide()
        self.ui.label_25.hide()
        self.ui.textBrowser.hide()
        self.ui.textBrowser_2.hide()

        # Create main layout for the settings page content
        settings_layout = QVBoxLayout(self.ui.frame_9)
        settings_layout.setContentsMargins(50, 80, 50, 50)
        settings_layout.setSpacing(30)

        # --- About Section ---
        about_group_box = QGroupBox("About", self.ui.frame_9)
        about_group_box.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid gray; border-radius: 5px; margin-top: 1ex; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }")
        about_layout = QVBoxLayout(about_group_box)
        about_layout.setContentsMargins(15, 20, 15, 15)

        # About the Application
        app_label = QLabel("BudgetPal is a desktop application designed to simplify personal finance. Track income, monitor expenses, and achieve savings goals.")
        app_label.setWordWrap(True)
        about_layout.addWidget(QLabel("<b>About the Application:</b>"))
        about_layout.addWidget(app_label)

        # About the Developers
        dev_info = """
        <b>Developed by:</b>
        - [Arbas, Jhon Eric]
        - [Acosta, Arjay]
        - [Danielle Gabriel]
        - [Cauilan, Crystle Joy]
        - [Escote, Elias]
        - [Magparangalan, Cyron Jhon]
        """
        dev_label = QLabel(dev_info)
        dev_label.setWordWrap(True)
        about_layout.addWidget(QLabel("<b>About the Developers:</b>"))
        about_layout.addWidget(dev_label)
        
        settings_layout.addWidget(about_group_box)

        # --- Data Management Section ---
        data_group_box = QGroupBox("Data Management", self.ui.frame_9)
        data_group_box.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid gray; border-radius: 5px; margin-top: 1ex; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }")
        data_layout = QVBoxLayout(data_group_box)
        data_layout.setContentsMargins(15, 20, 15, 15)

        # Clear All Data Button
        clear_data_label = QLabel("Permanently delete all income, expense, budget, and savings records. This action cannot be undone.")
        clear_data_label.setWordWrap(True)
        data_layout.addWidget(clear_data_label)
        self.clear_data_button = QPushButton("Clear All Application Data", data_group_box)
        self.clear_data_button.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; padding: 8px 15px; border-radius: 5px; } QPushButton:hover { background-color: #C0392B; }")
        self.clear_data_button.clicked.connect(self.confirm_clear_data)
        self.clear_data_button.setToolTip("Permanently delete all income and expense records")
        data_layout.addWidget(self.clear_data_button)

        # Placeholder for Export/Import
        export_import_layout = QHBoxLayout()
        self.export_data_button = QPushButton("Export Data", data_group_box)
        self.export_data_button.setStyleSheet("QPushButton { background-color: #3498DB; color: white; padding: 8px 15px; border-radius: 5px; } QPushButton:hover { background-color: #2980B9; }")
        self.export_data_button.clicked.connect(self.export_data_placeholder)
        export_import_layout.addWidget(self.export_data_button)

        self.import_data_button = QPushButton("Import Data", data_group_box)
        self.import_data_button.setStyleSheet("QPushButton { background-color: #3498DB; color: white; padding: 8px 15px; border-radius: 5px; } QPushButton:hover { background-color: #2980B9; }")
        self.import_data_button.clicked.connect(self.import_data_placeholder)
        export_import_layout.addWidget(self.import_data_button)
        
        data_layout.addLayout(export_import_layout)
        settings_layout.addWidget(data_group_box)

        # Add a stretch to push content to the top
        settings_layout.addStretch(1)

        # Set the layout for frame_9
        self.ui.frame_9.setLayout(settings_layout)


    def confirm_clear_data(self):
        reply = QMessageBox.warning(self, 'Confirm Deletion',
                                     "Are you sure you want to delete all your financial data? This action cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            db.delete_all_records(self.conn)
            self.refresh_all_data()
            QMessageBox.information(self, "Success", "All data has been cleared.")

    # Placeholder functions for export/import
    def export_data_placeholder(self):
        QMessageBox.information(self, "Feature Coming Soon", "Export Data functionality will be available in a future update!")

    def import_data_placeholder(self):
        QMessageBox.information(self, "Feature Coming Soon", "Import Data functionality will be available in a future update!")

    def refresh_all_data(self):
        self.load_expenses()
        self.load_income()
        self.load_budgets()
        self.load_savings()
        self.load_history()
        self.update_reports_page()
        self.update_dashboard_graph()
        self.update_expense_graph()
        self.update_dashboard_overview()
        print("UI Refreshed.")

    def update_dashboard_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        expense_data = db.get_expenses_by_category(self.conn)
        if not expense_data:
            ax.text(0.5, 0.5, 'No expense data to display',
                    ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
        else:
            ax.pie([x[1] for x in expense_data], labels=[x[0] for x in expense_data], autopct='%1.1f%%', startangle=90)
            # MODIFICATION: Use a figure suptitle instead of an axis title.
            self.figure.suptitle("Expense Breakdown")
        
        # The standard tight_layout() will now correctly adjust for the suptitle.
        self.figure.tight_layout()
        self.canvas.draw()

    def update_expense_graph(self):
        self.expense_figure.clear()
        ax = self.expense_figure.add_subplot(111)

        recent_expenses = db.get_recent_expenses(self.conn, limit=5)

        if not recent_expenses:
            ax.text(0.5, 0.5, 'No recent expenses to display',
                    ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
        else:
            recent_expenses.reverse()
            categories = [x[0] for x in recent_expenses]
            amounts = [x[1] for x in recent_expenses]

            ax.barh(categories, amounts, color='#7293CB')
            ax.set_title("5 Most Recent Expenses", fontsize=10)

            # Adjust fonts and spacing
            ax.tick_params(axis='y', labelsize=9)
            ax.tick_params(axis='x', labelsize=9)

            # Fix: set layout margins manually to avoid cutting
            self.expense_figure.subplots_adjust(left=0.35, right=0.95, top=0.88, bottom=0.15)

            # Optional: wrap long category names (if still cut off)
            wrapped_categories = [label if len(label) < 15 else '\n'.join(label[i:i+15] for i in range(0, len(label), 15)) for label in categories]
            ax.set_yticks(range(len(wrapped_categories)))
            ax.set_yticklabels(wrapped_categories)

        self.expense_canvas.draw()


    def update_dashboard_overview(self):
        recent_expenses = db.get_recent_expenses(self.conn, limit=3)
        recent_savings = db.get_recent_savings(self.conn, limit=3)

        overview_html = """
        <style>
            th { text-align: left; padding: 4px; border-bottom: 1px solid #EAECEE; color: #34495E; }
            td { padding: 4px; color: #566573; }
        </style>
        <table width="100%">
            <tr>
                <th width="50%">Recent Expenses</th>
                <th>Recent Savings Goals</th>
            </tr>
            <tr><td valign="top">
        """
        if not recent_expenses:
            overview_html += "No recent expenses."
        else:
            for expense in recent_expenses:
                overview_html += f"&bull; {expense[0]} (P{expense[1]:.2f})<br>"
        
        overview_html += '</td><td valign="top">'

        if not recent_savings:
            overview_html += "No recent savings goals."
        else:
            for goal in recent_savings:
                overview_html += f"&bull; {goal[0]}<br>"

        overview_html += "</td></tr></table>"
        self.overview_text.setHtml(overview_html)

    @pyqtSlot()
    def add_expense(self):
        amount_text = self.ui.lineEdit.text()
        category = self.ui.lineEdit_2.text()
        date = self.ui.dateTimeEdit.date().toString("yyyy-MM-dd")
        time = datetime.now().strftime("%H:%M:%S")
        if not amount_text or not category:
            QMessageBox.warning(self, "Input Error", "Amount and Category cannot be empty.")
            return
        try:
            expense = (float(amount_text), category, date, time)
            db.add_expense(self.conn, expense)
            self.ui.lineEdit.clear()
            self.ui.lineEdit_2.clear()
            self.refresh_all_data()
        except (ValueError, Exception) as e:
            QMessageBox.critical(self, "Error", f"Could not add expense: {e}")

    @pyqtSlot()
    def add_income(self):
        amount = self.ui.lineEdit_4.text()
        source = self.ui.lineEdit_5.text()
        date = self.income_date_picker.date().toString("yyyy-MM-dd")
        notes = self.ui.lineEdit_7.text()
        if not amount or not source:
            QMessageBox.warning(self, "Input Error", "Amount and Source are required.")
            return
        try:
            income_record = (float(amount), source, date, notes)
            db.add_income(self.conn, income_record)
            self.ui.lineEdit_4.clear()
            self.ui.lineEdit_5.clear()
            self.ui.lineEdit_7.clear()
            self.refresh_all_data()
        except (ValueError, Exception) as e:
            QMessageBox.critical(self, "Error", f"Could not add income: {e}")

    @pyqtSlot()
    def add_budget(self):
        name = self.ui.lineEdit_3.text()
        date = self.ui.dateTimeEdit_2.date().toString("yyyy-MM-dd")
        if not name:
            QMessageBox.warning(self, "Input Error", "Budget name cannot be empty.")
            return
        try:
            budget = (name, 0, date)
            db.add_budget(self.conn, budget)
            self.ui.lineEdit_3.clear()
            self.refresh_all_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not add budget: {e}")

    @pyqtSlot()
    def add_saving_goal(self):
        goal = self.ui.textEdit.toPlainText()
        if not goal:
            QMessageBox.warning(self, "Input Error", "Goal description cannot be empty.")
            return
        try:
            db.add_saving_goal(self.conn, (goal, datetime.now().strftime("%Y-%m-%d")))
            self.ui.textEdit.clear()
            self.refresh_all_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not add saving goal: {e}")

    def load_expenses(self):
        try:
            expenses = db.get_all_expenses(self.conn)
            self.ui.expenseTable.setRowCount(0)
            for r, rd in enumerate(expenses):
                self.ui.expenseTable.insertRow(r)
                for c, d in enumerate(rd): self.ui.expenseTable.setItem(r, c, QTableWidgetItem(str(d)))
        except Exception as e:
            print(f"Failed to load expenses: {e}")

    def load_income(self):
        try:
            total_income, total_expenses = db.get_total_income(self.conn), db.get_total_expenses(self.conn)
            self.ui.textBrowser_3.setText(f"P{total_income:.2f}")
            self.ui.textBrowser_4.setText(f"P{total_expenses:.2f}")
            self.ui.textBrowser_5.setText(f"P{total_income - total_expenses:.2f}")
            all_income = db.get_all_income(self.conn)
            self.income_history_table.setRowCount(0)
            for row_num, row_data in enumerate(all_income):
                self.income_history_table.insertRow(row_num)
                for col_num, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.income_history_table.setItem(row_num, col_num, item)
        except Exception as e:
            print(f"Failed to load income: {e}")

    def load_budgets(self):
        try:
            budgets = db.get_all_budgets(self.conn)
            self.ui.tableWidget.setRowCount(0); self.ui.tableWidget_2.setRowCount(0)
            for r, rd in enumerate(budgets):
                self.ui.tableWidget.insertRow(r); self.ui.tableWidget_2.insertRow(r)
                for c, d in enumerate(rd):
                    self.ui.tableWidget.setItem(r, c, QTableWidgetItem(str(d)))
                    self.ui.tableWidget_2.setItem(r, c, QTableWidgetItem(str(d)))
        except Exception as e:
            print(f"Failed to load budgets: {e}")

    def load_savings(self):
        try:
            self.ui.tableWidget_3.setWordWrap(True)
            self.ui.tableWidget_3.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            goals = db.get_all_savings_goals(self.conn)
            self.ui.tableWidget_3.setRowCount(0)
            for row_num, row_data in enumerate(goals):
                self.ui.tableWidget_3.insertRow(row_num)
                for col_num, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.ui.tableWidget_3.setItem(row_num, col_num, item)
                self.ui.tableWidget_3.resizeRowToContents(row_num)
        except Exception as e:
            print(f"Failed to load savings: {e}")

    def load_history(self):
        try:
            transactions = db.get_all_transactions(self.conn)
            self.ui.tableWidget_4.setRowCount(0)
            for r, rd in enumerate(transactions):
                self.ui.tableWidget_4.insertRow(r)
                self.ui.tableWidget_4.setItem(r, 0, QTableWidgetItem(str(rd[1])))
                self.ui.tableWidget_4.setItem(r, 1, QTableWidgetItem(str(rd[2])))
                self.ui.tableWidget_4.setItem(r, 2, QTableWidgetItem(str(rd[0])))
        except Exception as e:
            print(f"Failed to load history: {e}")

    def update_reports_page(self):
        self.bar_figure.clear()
        ax1 = self.bar_figure.add_subplot(111)
        total_income = db.get_total_income(self.conn)
        total_expenses = db.get_total_expenses(self.conn)
        ax1.bar(['Income', 'Expenses'], [total_income, total_expenses], color=['#2ECC71', '#E74C3C'])
        ax1.set_title('Total Income vs. Expenses')
        ax1.set_ylabel('Amount (P)')
        self.bar_figure.tight_layout()
        self.bar_canvas.draw()
        self.pie_figure.clear()
        ax2 = self.pie_figure.add_subplot(111)
        top_expenses = db.get_top_expenses(self.conn)
        if not top_expenses:
            ax2.text(0.5, 0.5, 'No expense data to display',
                     ha='center', va='center', transform=ax2.transAxes)
            ax2.axis('off')
        else:
            ax2.pie([x[1] for x in top_expenses], labels=[x[0] for x in top_expenses], autopct='%1.1f%%', startangle=90)
            ax2.set_title('Top 5 Expense Categories')
        self.pie_figure.tight_layout()
        self.pie_canvas.draw()
        print("Reports page updated.")

    def on_dashboard_btn2_toggled(self, c):
        if c: self.ui.stackedWidget.setCurrentIndex(0)
    def on_income_btn2_toggled(self, c):
        if c: self.ui.stackedWidget.setCurrentIndex(1)
    def on_expense_btn2_toggled(self, c):
        if c: self.ui.stackedWidget.setCurrentIndex(2)
    def on_budget_btn2_toggled(self, c):
        if c: self.ui.stackedWidget.setCurrentIndex(3)
    def on_savings_btn2_toggled(self, c):
        if c: self.ui.stackedWidget.setCurrentIndex(4)
    def on_reports_btn2_toggled(self, c):
        if c: self.ui.stackedWidget.setCurrentIndex(5)
    def on_history_btn2_toggled(self, c):
        if c: self.ui.stackedWidget.setCurrentIndex(6)
    def on_setting_btn2_toggled(self, c):
        if c: self.ui.stackedWidget.setCurrentIndex(7)
        
    def closeEvent(self, event):
        if self.conn: self.conn.close()
        super().closeEvent(event)
        
    def setup_reports_page(self):
        self.ui.frame_158.hide()
        self.ui.frame_160.hide()
        self.ui.frame_178.hide()
        self.ui.frame_180.hide()

        # Create a layout widget container for charts
        report_layout_container = QWidget(self.ui.frame_7)
        report_layout_container.setGeometry(QRect(20, 70, 600, 420))
        layout = QVBoxLayout(report_layout_container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        # Bar Chart Section
        self.bar_figure = plt.figure(figsize=(5, 2.5))
        self.bar_canvas = FigureCanvas(self.bar_figure)
        layout.addWidget(self.bar_canvas)

        # Pie Chart Section
        self.pie_figure = plt.figure(figsize=(5, 2.5))
        self.pie_canvas = FigureCanvas(self.pie_figure)
        layout.addWidget(self.pie_canvas)

    def update_reports_page(self):
        self.bar_figure.clear()
        ax1 = self.bar_figure.add_subplot(111)
        total_income = db.get_total_income(self.conn)
        total_expenses = db.get_total_expenses(self.conn)
        ax1.bar(['Income', 'Expenses'], [total_income, total_expenses], color=['#2ECC71', '#E74C3C'])
        ax1.set_title('Total Income vs. Expenses')
        ax1.set_ylabel('Amount (PHP)')
        self.bar_figure.tight_layout()
        self.bar_canvas.draw()

        self.pie_figure.clear()
        ax2 = self.pie_figure.add_subplot(111)
        top_expenses = db.get_top_expenses(self.conn)
        if not top_expenses:
            ax2.text(0.5, 0.5, 'No expense data to display',
                     ha='center', va='center', transform=ax2.transAxes)
            ax2.axis('off')
        else:
            ax2.pie([x[1] for x in top_expenses],
                    labels=[x[0] for x in top_expenses],
                    autopct='%1.1f%%',
                    startangle=90)
            ax2.set_title('Top 5 Expense Categories')
        self.pie_figure.tight_layout()
        self.pie_canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())