"""
TRIZ-Based Project Management Dashboard
A comprehensive PyQt5 application for managing scientific projects with TRIZ methodology integration.
Features: Project management, problem definition, contradiction analysis, TRIZ principles, progress tracking.
"""

import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from enum import Enum

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
    QTextEdit, QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit,
    QFileDialog, QMessageBox, QDialog, QListWidget, QListWidgetItem,
    QScrollArea, QGridLayout, QGroupBox, QCheckBox, QFormLayout,
    QSplitter, QFrame, QHeaderView, QProgressBar, QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QBrush, QTextCursor
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis


# TRIZ Principles Database
TRIZ_PRINCIPLES = {
    1: ("Segmentation", "Divide an object into parts; make an object easy to disassemble; increase the degree of fragmentation or segmentation."),
    2: ("Taking Out", "Remove a disturbing part or property from an object; extract the 'useful' part or property from an object."),
    3: ("Local Quality", "Change an object's structure from uniform to non-uniform; make each part of an object function in conditions most suitable for it."),
    4: ("Asymmetry", "Break the symmetry of an object; if an object is asymmetrical, increase its degree of asymmetry."),
    5: ("Merging", "Combine identical or similar objects, assemble identical parts to perform parallel operations; merge homogeneous objects or operations."),
    6: ("Universality", "Make an object perform multiple functions; eliminate the need for other objects by adding new functions."),
    7: ("Nesting", "Place objects inside other objects; place each object, as far as possible, inside another object."),
    8: ("Anti-weight", "Compensate for the weight of an object by merging with the environment; make it interact with the environment (e.g., buoyancy)."),
    9: ("Preliminary Tension", "Pre-stress an object before it is used; pre-arrange objects so they can work without delay and handle harmful effects."),
    10: ("Preliminary Action", "Perform, before it is needed, the required change of an object; pre-arrange objects such that they can go into action without delay."),
    11: ("Beforehand Cushioning", "Prepare emergency means beforehand; compensate for the relatively low reliability of an object by countermeasures prepared in advance."),
    12: ("Equipotentiality", "In a potential field, limit position changes (e.g., change operating conditions to eliminate the need to maintain object balance)."),
    13: ("The Other Way Around", "Invert the action(s) used to solve the problem; reverse the direction of motion of an object; turn the object 'inside out'."),
    14: ("Spheroidality", "Replace linear parts or surfaces of an object with curved ones; replace flat surfaces with spherical surfaces; use rollers, balls, spirals."),
    15: ("Dynamics", "Allow (or design for) the characteristics of an object, external environment, or process to change to be optimal at each stage of operation."),
    16: ("Partial or Excessive Action", "If it is difficult to achieve 100% of an effect, achieve somewhat less or more by the same object; overdose on the desired property."),
    17: ("Transition to a New Dimension", "Move the problem into a new dimension; use a multi-story arrangement of objects instead of a single-story arrangement."),
    18: ("Mechanical Vibration", "Cause an object to oscillate or vibrate; increase its frequency of oscillation (ultrasonic oscillations); use the object's resonant frequency."),
    19: ("Periodic Action", "Instead of continuous action, apply periodic or pulsed actions; if an action is already periodic, change the frequency; use pauses between impulses."),
    20: ("Continuity of Useful Action", "Carry on work continuously; make all parts of an object work at full load, all of the time; eliminate all idle or intermittent actions or work."),
    21: ("Rushing Through", "Conduct a process, or cause an object to move, at high speed; increase the speed of an object or process; accelerate the transition."),
    22: ("'Blessing in Disguise' or Convert Harm to Benefit", "Convert harmful factors into useful ones; eliminate the primary harmful action by adding it to another harmful action to resolve the problem."),
    23: ("Feedback", "Introduce feedback; make changes in a process depending on the results produced; establish monitoring and control."),
    24: ("Mediator", "Use an intermediary object or process; use a mediator to combine two objects or processes that are difficult to combine directly."),
    25: ("Self-Service", "Make an object serve itself by exploiting its own resources; increase the degree of an object's self-regulation, self-service, and self-control."),
    26: ("Copying", "Instead of an unavailable, expensive, fragile object, use simpler and inexpensive copies; replace an object, process, or property by optical copies or images."),
    27: ("Cheap Short-Living Objects", "Replace an expensive object with a multiple of inexpensive objects, compromising certain qualities (such as longevity)."),
    28: ("Mechanics Substitution", "Replace a mechanical means with a sensory (optical, acoustic, taste) means; use electric, magnetic and electromagnetic fields to interact with the object."),
    29: ("Pneumatics and Hydraulics", "Use gas and liquid parts of an object instead of solid parts; use inflatable or hydro-cushioned elements instead of rigid structures."),
    30: ("Flexible Shells and Thin Films", "Use flexible shells and thin films instead of three-dimensional rigid structures; isolate the object from the external environment using flexible shells and thin films."),
    31: ("Porous Materials", "Make an object porous or use porous materials; if an object is already porous, use the pores to introduce a useful substance or property."),
    32: ("Color Changes", "Change the color of an object or its external environment; change the transparency of an object or its external environment."),
    33: ("Homogeneity", "Make objects interact with a given object of the same material (or material with identical properties); change the external environment or process to use a homogeneous material."),
    34: ("Discarding and Recovering", "Make portions of an object that have fulfilled their functions go away (discard by dissolving, evaporating, etc.) or modify them during operation."),
    35: ("Parameter Changes", "Change an object's physical state (e.g., to a gas, liquid, or solid); change the concentration or consistency; change the degree of flexibility."),
    36: ("Phase Transition", "Use phenomena occurring during phase transition (e.g., volume changes, loss or absorption of heat)."),
    37: ("Thermal Expansion", "Use thermal expansion (or contraction) of materials; if thermal expansion is being used, use multiple materials with different thermal expansion coefficients."),
    38: ("Strong Oxidants", "Replace common air with oxygen-enriched air; replace enriched air with pure oxygen; ionize the air or oxygen; use ionized (or ozonized) oxygen."),
    39: ("Inert Atmosphere", "Replace a normal environment with an inert one; add neutral parts, or inert additives to an object."),
    40: ("Composite Materials", "Change from uniform to composite (multiple) materials; use composite materials instead of homogeneous materials."),
}

# Engineering Characteristics for Contradiction Matrix
ENGINEERING_CHARACTERISTICS = [
    "Weight", "Length", "Area", "Volume", "Speed", "Force", "Tension/Pressure",
    "Temperature", "Brightness", "Energy", "Power", "Noise", "Harmful effects",
    "Reliability", "Accuracy", "Friction", "Shape complexity", "Stability",
    "Number of operations", "Serviceability", "Ease of assembly", "Ease of repair",
    "Aesthetics", "Toxicity", "Cost", "Duration of action", "Productivity"
]


class ProjectStatus(Enum):
    """Project status enumeration"""
    PLANNING = "Planning"
    ANALYSIS = "Analysis"
    DESIGN = "Design"
    PROTOTYPING = "Prototyping"
    TESTING = "Testing"
    OPTIMIZATION = "Optimization"
    COMPLETED = "Completed"


class DatabaseManager:
    """Manages SQLite database for project storage"""
    
    def __init__(self, db_path="triz_projects.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT,
                created_date TEXT,
                start_date TEXT,
                target_date TEXT,
                progress INTEGER DEFAULT 0,
                category TEXT
            )
        """)
        
        # Problems table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                problem_statement TEXT,
                problem_analysis TEXT,
                ideal_final_result TEXT,
                created_date TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        # Contradictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contradictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                improving_parameter TEXT,
                worsening_parameter TEXT,
                triz_principles TEXT,
                solution TEXT,
                created_date TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        # Resources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                resource_name TEXT,
                resource_type TEXT,
                description TEXT,
                status TEXT,
                created_date TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        # Design Features table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS design_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                feature_name TEXT,
                description TEXT,
                implementation_notes TEXT,
                status TEXT,
                created_date TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        # Progress Notes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                note_date TEXT,
                content TEXT,
                milestone TEXT,
                created_date TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_project(self, name, description, status, category):
        """Add a new project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (name, description, status, category, created_date)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, status, category, datetime.now().isoformat()))
        conn.commit()
        project_id = cursor.lastrowid
        conn.close()
        return project_id
    
    def get_projects(self):
        """Retrieve all projects"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY created_date DESC")
        projects = cursor.fetchall()
        conn.close()
        return projects
    
    def get_project(self, project_id):
        """Retrieve a specific project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project = cursor.fetchone()
        conn.close()
        return project
    
    def update_project(self, project_id, **kwargs):
        """Update project information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [project_id]
        
        cursor.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
    
    def delete_project(self, project_id):
        """Delete a project and related data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete all related data
        cursor.execute("DELETE FROM problems WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM contradictions WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM resources WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM design_features WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM progress_notes WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        
        conn.commit()
        conn.close()
    
    def insert_record(self, table, **kwargs):
        """Insert a record into any table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        keys = list(kwargs.keys())
        values = list(kwargs.values())
        placeholders = ", ".join(["?"] * len(keys))
        
        cursor.execute(f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({placeholders})", values)
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_records(self, table, project_id=None):
        """Retrieve records from a table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if project_id:
            cursor.execute(f"SELECT * FROM {table} WHERE project_id = ? ORDER BY created_date DESC", (project_id,))
        else:
            cursor.execute(f"SELECT * FROM {table} ORDER BY created_date DESC")
        
        records = cursor.fetchall()
        conn.close()
        return records


class ProjectManagerTab(QWidget):
    """Tab for project management"""
    
    project_selected = pyqtSignal(int)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_project_id = None
        self.init_ui()
        self.load_projects()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Top panel for adding new project
        top_panel = QGroupBox("New Project")
        top_layout = QGridLayout()
        
        top_layout.addWidget(QLabel("Project Name:"), 0, 0)
        self.project_name = QLineEdit()
        top_layout.addWidget(self.project_name, 0, 1)
        
        top_layout.addWidget(QLabel("Category:"), 0, 2)
        self.category = QComboBox()
        self.category.addItems(["Electronics", "Mechanical", "Software", "Biotech", "Materials", "Other"])
        top_layout.addWidget(self.category, 0, 3)
        
        top_layout.addWidget(QLabel("Description:"), 1, 0)
        self.project_desc = QTextEdit()
        self.project_desc.setMaximumHeight(80)
        top_layout.addWidget(self.project_desc, 1, 1, 1, 3)
        
        add_btn = QPushButton("Create Project")
        add_btn.clicked.connect(self.add_project)
        top_layout.addWidget(add_btn, 2, 3)
        
        top_panel.setLayout(top_layout)
        layout.addWidget(top_panel)
        
        # Projects table
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(6)
        self.projects_table.setHorizontalHeaderLabels(["ID", "Name", "Status", "Category", "Progress", "Created"])
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.projects_table.itemSelectionChanged.connect(self.on_project_selected)
        layout.addWidget(self.projects_table)
        
        # Project control buttons
        btn_layout = QHBoxLayout()
        
        update_btn = QPushButton("Update Status")
        update_btn.clicked.connect(self.update_project_status)
        btn_layout.addWidget(update_btn)
        
        delete_btn = QPushButton("Delete Project")
        delete_btn.clicked.connect(self.delete_project)
        btn_layout.addWidget(delete_btn)
        
        export_btn = QPushButton("Export Project")
        export_btn.clicked.connect(self.export_project)
        btn_layout.addWidget(export_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def add_project(self):
        """Add a new project"""
        name = self.project_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Please enter a project name")
            return
        
        description = self.project_desc.toPlainText().strip()
        category = self.category.currentText()
        status = ProjectStatus.PLANNING.value
        
        self.db.add_project(name, description, status, category)
        self.load_projects()
        
        self.project_name.clear()
        self.project_desc.clear()
        QMessageBox.information(self, "Success", "Project created successfully!")
    
    def load_projects(self):
        """Load and display all projects"""
        projects = self.db.get_projects()
        self.projects_table.setRowCount(len(projects))
        
        for row, project in enumerate(projects):
            for col, value in enumerate(project):
                if col == 5:  # Format date
                    value = value[:10] if value else ""
                item = QTableWidgetItem(str(value))
                item.setData(Qt.UserRole, project[0])  # Store project ID
                self.projects_table.setItem(row, col, item)
    
    def on_project_selected(self):
        """Handle project selection"""
        selected = self.projects_table.selectedItems()
        if selected:
            self.current_project_id = selected[0].data(Qt.UserRole)
            self.project_selected.emit(self.current_project_id)
    
    def update_project_status(self):
        """Update project status"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection", "Please select a project first")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Project Status")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("New Status:"))
        status_combo = QComboBox()
        status_combo.addItems([s.value for s in ProjectStatus])
        layout.addWidget(status_combo)
        
        layout.addWidget(QLabel("Progress (%):"))
        progress_spin = QSpinBox()
        progress_spin.setMaximum(100)
        layout.addWidget(progress_spin)
        
        ok_btn = QPushButton("Update")
        ok_btn.clicked.connect(lambda: self.confirm_update(dialog, status_combo, progress_spin))
        layout.addWidget(ok_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def confirm_update(self, dialog, status_combo, progress_spin):
        """Confirm status update"""
        status = status_combo.currentText()
        progress = progress_spin.value()
        
        self.db.update_project(self.current_project_id, status=status, progress=progress)
        self.load_projects()
        dialog.accept()
        QMessageBox.information(self, "Success", "Project updated!")
    
    def delete_project(self):
        """Delete selected project"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection", "Please select a project first")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", "Delete this project and all related data?")
        if reply == QMessageBox.Yes:
            self.db.delete_project(self.current_project_id)
            self.load_projects()
            QMessageBox.information(self, "Success", "Project deleted!")
    
    def export_project(self):
        """Export project data as JSON"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection", "Please select a project first")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Project", "", "JSON Files (*.json)")
        if not filepath:
            return
        
        project = self.db.get_project(self.current_project_id)
        problems = self.db.get_records("problems", self.current_project_id)
        contradictions = self.db.get_records("contradictions", self.current_project_id)
        resources = self.db.get_records("resources", self.current_project_id)
        design_features = self.db.get_records("design_features", self.current_project_id)
        progress_notes = self.db.get_records("progress_notes", self.current_project_id)
        
        data = {
            "project": project,
            "problems": problems,
            "contradictions": contradictions,
            "resources": resources,
            "design_features": design_features,
            "progress_notes": progress_notes
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        QMessageBox.information(self, "Success", "Project exported successfully!")


class ProblemAnalysisTab(QWidget):
    """Tab for problem definition and analysis"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_project_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Problem input
        form_group = QGroupBox("Problem Definition")
        form_layout = QFormLayout()
        
        self.problem_input = QTextEdit()
        self.problem_input.setPlaceholderText("Describe the problem you're trying to solve...")
        form_layout.addRow("Problem Statement:", self.problem_input)
        
        self.analysis_input = QTextEdit()
        self.analysis_input.setPlaceholderText("Analyze the root causes and context...")
        form_layout.addRow("Problem Analysis:", self.analysis_input)
        
        self.ideal_result = QTextEdit()
        self.ideal_result.setPlaceholderText("Define the ideal final result (IFR)...")
        form_layout.addRow("Ideal Final Result:", self.ideal_result)
        
        save_btn = QPushButton("Save Problem Definition")
        save_btn.clicked.connect(self.save_problem)
        form_layout.addRow("", save_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Problems history
        self.problems_list = QListWidget()
        self.problems_list.itemSelectionChanged.connect(self.load_problem)
        layout.addWidget(QLabel("Previous Problems:"))
        layout.addWidget(self.problems_list)
        
        self.setLayout(layout)
    
    def set_current_project(self, project_id):
        """Set current project"""
        self.current_project_id = project_id
        self.load_problems()
    
    def save_problem(self):
        """Save problem definition"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection", "Please select a project first")
            return
        
        problem = self.problem_input.toPlainText().strip()
        if not problem:
            QMessageBox.warning(self, "Validation", "Please enter a problem statement")
            return
        
        analysis = self.analysis_input.toPlainText().strip()
        ideal = self.ideal_result.toPlainText().strip()
        
        self.db.insert_record("problems",
            project_id=self.current_project_id,
            problem_statement=problem,
            problem_analysis=analysis,
            ideal_final_result=ideal,
            created_date=datetime.now().isoformat()
        )
        
        self.load_problems()
        QMessageBox.information(self, "Success", "Problem definition saved!")
    
    def load_problems(self):
        """Load problems for current project"""
        self.problems_list.clear()
        if not self.current_project_id:
            return
        
        problems = self.db.get_records("problems", self.current_project_id)
        for problem in problems:
            item = QListWidgetItem(problem[2][:50] + "...")
            item.setData(Qt.UserRole, problem)
            self.problems_list.addItem(item)
    
    def load_problem(self):
        """Load selected problem details"""
        item = self.problems_list.currentItem()
        if not item:
            return
        
        problem = item.data(Qt.UserRole)
        self.problem_input.setText(problem[2])
        self.analysis_input.setText(problem[3])
        self.ideal_result.setText(problem[4])


class ContradictionAnalysisTab(QWidget):
    """Tab for TRIZ contradiction analysis"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_project_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        main_layout = QHBoxLayout()
        
        # Left panel - contradiction input
        left_panel = QGroupBox("Contradiction Definition")
        left_layout = QFormLayout()
        
        self.improving_param = QComboBox()
        self.improving_param.addItems(ENGINEERING_CHARACTERISTICS)
        left_layout.addRow("Improving Parameter:", self.improving_param)
        
        self.worsening_param = QComboBox()
        self.worsening_param.addItems(ENGINEERING_CHARACTERISTICS)
        left_layout.addRow("Worsening Parameter:", self.worsening_param)
        
        analyze_btn = QPushButton("Get TRIZ Principles")
        analyze_btn.clicked.connect(self.analyze_contradiction)
        left_layout.addRow("", analyze_btn)
        
        self.solution_input = QTextEdit()
        self.solution_input.setPlaceholderText("Proposed solution based on TRIZ principles...")
        left_layout.addRow("Solution:", self.solution_input)
        
        save_btn = QPushButton("Save Contradiction")
        save_btn.clicked.connect(self.save_contradiction)
        left_layout.addRow("", save_btn)
        
        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel)
        
        # Right panel - TRIZ principles
        right_panel = QGroupBox("Applicable TRIZ Principles")
        right_layout = QVBoxLayout()
        
        self.principles_list = QListWidget()
        right_layout.addWidget(self.principles_list)
        
        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel)
        
        widget = QWidget()
        widget.setLayout(main_layout)
        
        main_vertical = QVBoxLayout()
        main_vertical.addWidget(widget)
        
        # Contradictions history
        self.contradictions_list = QListWidget()
        self.contradictions_list.itemSelectionChanged.connect(self.load_contradiction)
        main_vertical.addWidget(QLabel("Previous Contradictions:"))
        main_vertical.addWidget(self.contradictions_list)
        
        self.setLayout(main_vertical)
    
    def set_current_project(self, project_id):
        """Set current project"""
        self.current_project_id = project_id
        self.load_contradictions()
    
    def analyze_contradiction(self):
        """Analyze contradiction using TRIZ principles"""
        improving = self.improving_param.currentText()
        worsening = self.worsening_param.currentText()
        
        # Simplified TRIZ contradiction matrix (in practice, use full matrix)
        # This shows applicable principles based on typical patterns
        principles_map = {
            ("Weight", "Speed"): [1, 8, 14, 15],
            ("Speed", "Accuracy"): [3, 15, 19, 35],
            ("Cost", "Quality"): [1, 5, 6, 27],
            ("Complexity", "Simplicity"): [2, 7, 13, 33],
        }
        
        key = (improving, worsening)
        principles = principles_map.get(key, [1, 6, 10, 15, 28])  # Default principles
        
        self.principles_list.clear()
        for principle_num in principles:
            principle = TRIZ_PRINCIPLES[principle_num]
            text = f"{principle_num}. {principle[0]}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, principle[1])
            self.principles_list.addItem(item)
        
        if self.principles_list.count() > 0:
            self.principles_list.itemClicked.emit(self.principles_list.item(0))
    
    def load_contradiction(self):
        """Load selected contradiction"""
        item = self.contradictions_list.currentItem()
        if not item:
            return
        
        contradiction = item.data(Qt.UserRole)
        self.improving_param.setCurrentText(contradiction[2])
        self.worsening_param.setCurrentText(contradiction[3])
        self.solution_input.setText(contradiction[5])
    
    def save_contradiction(self):
        """Save contradiction analysis"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection", "Please select a project first")
            return
        
        improving = self.improving_param.currentText()
        worsening = self.worsening_param.currentText()
        solution = self.solution_input.toPlainText().strip()
        
        principles = []
        for i in range(self.principles_list.count()):
            item = self.principles_list.item(i)
            principles.append(item.text())
        
        self.db.insert_record("contradictions",
            project_id=self.current_project_id,
            improving_parameter=improving,
            worsening_parameter=worsening,
            triz_principles=json.dumps(principles),
            solution=solution,
            created_date=datetime.now().isoformat()
        )
        
        self.load_contradictions()
        QMessageBox.information(self, "Success", "Contradiction analysis saved!")
    
    def load_contradictions(self):
        """Load contradictions for current project"""
        self.contradictions_list.clear()
        if not self.current_project_id:
            return
        
        contradictions = self.db.get_records("contradictions", self.current_project_id)
        for contradiction in contradictions:
            text = f"{contradiction[2]} ↔ {contradiction[3]}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, contradiction)
            self.contradictions_list.addItem(item)


class ResourceAnalysisTab(QWidget):
    """Tab for resource analysis (Substance-Field analysis)"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_project_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Add resource
        form_group = QGroupBox("Add Resource/Substance")
        form_layout = QFormLayout()
        
        self.resource_name = QLineEdit()
        form_layout.addRow("Resource Name:", self.resource_name)
        
        self.resource_type = QComboBox()
        self.resource_type.addItems(["Material", "Energy", "Information", "Space", "Time", "Other"])
        form_layout.addRow("Type:", self.resource_type)
        
        self.resource_desc = QTextEdit()
        self.resource_desc.setMaximumHeight(80)
        form_layout.addRow("Description:", self.resource_desc)
        
        add_btn = QPushButton("Add Resource")
        add_btn.clicked.connect(self.add_resource)
        form_layout.addRow("", add_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Resources table
        self.resources_table = QTableWidget()
        self.resources_table.setColumnCount(5)
        self.resources_table.setHorizontalHeaderLabels(["Name", "Type", "Description", "Status", "Date"])
        self.resources_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.resources_table)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("Delete Resource")
        delete_btn.clicked.connect(self.delete_resource)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def set_current_project(self, project_id):
        """Set current project"""
        self.current_project_id = project_id
        self.load_resources()
    
    def add_resource(self):
        """Add a new resource"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection", "Please select a project first")
            return
        
        name = self.resource_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Please enter resource name")
            return
        
        resource_type = self.resource_type.currentText()
        description = self.resource_desc.toPlainText().strip()
        
        self.db.insert_record("resources",
            project_id=self.current_project_id,
            resource_name=name,
            resource_type=resource_type,
            description=description,
            status="Available",
            created_date=datetime.now().isoformat()
        )
        
        self.load_resources()
        self.resource_name.clear()
        self.resource_desc.clear()
        QMessageBox.information(self, "Success", "Resource added!")
    
    def load_resources(self):
        """Load resources for current project"""
        resources = self.db.get_records("resources", self.current_project_id) if self.current_project_id else []
        self.resources_table.setRowCount(len(resources))
        
        for row, resource in enumerate(resources):
            for col in range(5):
                value = resource[col + 2] if col < 4 else resource[6][:10]
                item = QTableWidgetItem(str(value))
                item.setData(Qt.UserRole, resource[0])
                self.resources_table.setItem(row, col, item)
    
    def delete_resource(self):
        """Delete selected resource"""
        selected = self.resources_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Selection", "Please select a resource")
            return
        
        resource_id = selected[0].data(Qt.UserRole)
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
        conn.commit()
        conn.close()
        
        self.load_resources()
        QMessageBox.information(self, "Success", "Resource deleted!")


class DesignFeaturesTab(QWidget):
    """Tab for design features and prototyping"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_project_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Add design feature
        form_group = QGroupBox("Design Feature")
        form_layout = QFormLayout()
        
        self.feature_name = QLineEdit()
        form_layout.addRow("Feature Name:", self.feature_name)
        
        self.feature_desc = QTextEdit()
        self.feature_desc.setMaximumHeight(80)
        form_layout.addRow("Description:", self.feature_desc)
        
        self.impl_notes = QTextEdit()
        self.impl_notes.setMaximumHeight(80)
        form_layout.addRow("Implementation Notes:", self.impl_notes)
        
        self.feature_status = QComboBox()
        self.feature_status.addItems(["Conceptual", "In Progress", "Prototyped", "Testing", "Implemented", "Optimizing"])
        form_layout.addRow("Status:", self.feature_status)
        
        add_btn = QPushButton("Save Feature")
        add_btn.clicked.connect(self.save_feature)
        form_layout.addRow("", add_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Features table
        self.features_table = QTableWidget()
        self.features_table.setColumnCount(5)
        self.features_table.setHorizontalHeaderLabels(["Name", "Description", "Implementation", "Status", "Date"])
        self.features_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.features_table)
        
        self.setLayout(layout)
    
    def set_current_project(self, project_id):
        """Set current project"""
        self.current_project_id = project_id
        self.load_features()
    
    def save_feature(self):
        """Save design feature"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection", "Please select a project first")
            return
        
        name = self.feature_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Please enter feature name")
            return
        
        description = self.feature_desc.toPlainText().strip()
        impl = self.impl_notes.toPlainText().strip()
        status = self.feature_status.currentText()
        
        self.db.insert_record("design_features",
            project_id=self.current_project_id,
            feature_name=name,
            description=description,
            implementation_notes=impl,
            status=status,
            created_date=datetime.now().isoformat()
        )
        
        self.load_features()
        self.feature_name.clear()
        self.feature_desc.clear()
        self.impl_notes.clear()
        QMessageBox.information(self, "Success", "Feature saved!")
    
    def load_features(self):
        """Load design features"""
        features = self.db.get_records("design_features", self.current_project_id) if self.current_project_id else []
        self.features_table.setRowCount(len(features))
        
        for row, feature in enumerate(features):
            items_data = [feature[2], feature[3], feature[4], feature[5], feature[6][:10]]
            for col, value in enumerate(items_data):
                item = QTableWidgetItem(str(value))
                self.features_table.setItem(row, col, item)


class ProgressTrackingTab(QWidget):
    """Tab for progress tracking and milestones"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_project_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Progress note input
        form_group = QGroupBox("Add Progress Note")
        form_layout = QFormLayout()
        
        self.milestone_input = QLineEdit()
        self.milestone_input.setPlaceholderText("e.g., Prototype v1 completed")
        form_layout.addRow("Milestone:", self.milestone_input)
        
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Describe what was accomplished, challenges, next steps...")
        self.note_input.setMaximumHeight(100)
        form_layout.addRow("Progress Note:", self.note_input)
        
        save_btn = QPushButton("Add Note")
        save_btn.clicked.connect(self.add_note)
        form_layout.addRow("", save_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Progress notes display
        self.notes_list = QListWidget()
        self.notes_list.itemSelectionChanged.connect(self.display_note)
        layout.addWidget(QLabel("Progress Timeline:"))
        layout.addWidget(self.notes_list)
        
        # Note details
        self.note_details = QTextEdit()
        self.note_details.setReadOnly(True)
        layout.addWidget(QLabel("Note Details:"))
        layout.addWidget(self.note_details)
        
        self.setLayout(layout)
    
    def set_current_project(self, project_id):
        """Set current project"""
        self.current_project_id = project_id
        self.load_notes()
    
    def add_note(self):
        """Add a progress note"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Selection", "Please select a project first")
            return
        
        milestone = self.milestone_input.text().strip()
        content = self.note_input.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, "Validation", "Please enter a progress note")
            return
        
        self.db.insert_record("progress_notes",
            project_id=self.current_project_id,
            note_date=datetime.now().isoformat(),
            content=content,
            milestone=milestone,
            created_date=datetime.now().isoformat()
        )
        
        self.load_notes()
        self.milestone_input.clear()
        self.note_input.clear()
        QMessageBox.information(self, "Success", "Progress note added!")
    
    def load_notes(self):
        """Load progress notes"""
        self.notes_list.clear()
        if not self.current_project_id:
            return
        
        notes = self.db.get_records("progress_notes", self.current_project_id)
        for note in notes:
            date = note[2][:10]
            milestone = note[4] if note[4] else "Update"
            text = f"[{date}] {milestone}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, note)
            self.notes_list.addItem(item)
    
    def display_note(self):
        """Display selected note details"""
        item = self.notes_list.currentItem()
        if not item:
            return
        
        note = item.data(Qt.UserRole)
        self.note_details.setText(note[3])


class TRIZPrinciplesTab(QWidget):
    """Tab for browsing and learning TRIZ principles"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout()
        
        # Principles list
        self.principles_list = QListWidget()
        self.principles_list.itemSelectionChanged.connect(self.show_principle)
        
        for num, (name, _) in TRIZ_PRINCIPLES.items():
            text = f"{num}. {name}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, num)
            self.principles_list.addItem(item)
        
        layout.addWidget(QLabel("TRIZ Principles:"))
        layout.addWidget(self.principles_list)
        
        # Principle details
        right_layout = QVBoxLayout()
        
        self.principle_title = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.principle_title.setFont(font)
        right_layout.addWidget(self.principle_title)
        
        self.principle_desc = QTextEdit()
        self.principle_desc.setReadOnly(True)
        right_layout.addWidget(self.principle_desc)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        layout.addWidget(right_widget)
        
        self.setLayout(layout)
        
        # Select first principle
        if self.principles_list.count() > 0:
            self.principles_list.setCurrentRow(0)
    
    def show_principle(self):
        """Show selected principle details"""
        item = self.principles_list.currentItem()
        if not item:
            return
        
        principle_num = item.data(Qt.UserRole)
        name, description = TRIZ_PRINCIPLES[principle_num]
        
        self.principle_title.setText(f"{principle_num}. {name}")
        self.principle_desc.setText(description)


class TRIZDashboard(QMainWindow):
    """Main dashboard window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TRIZ Scientific Project Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        
        self.db = DatabaseManager()
        
        # Create tabs
        tabs = QTabWidget()
        
        self.project_tab = ProjectManagerTab(self.db)
        self.problem_tab = ProblemAnalysisTab(self.db)
        self.contradiction_tab = ContradictionAnalysisTab(self.db)
        self.resource_tab = ResourceAnalysisTab(self.db)
        self.design_tab = DesignFeaturesTab(self.db)
        self.progress_tab = ProgressTrackingTab(self.db)
        self.principles_tab = TRIZPrinciplesTab()
        
        tabs.addTab(self.project_tab, "Projects")
        tabs.addTab(self.problem_tab, "Problem Analysis")
        tabs.addTab(self.contradiction_tab, "Contradictions")
        tabs.addTab(self.resource_tab, "Resources")
        tabs.addTab(self.design_tab, "Design Features")
        tabs.addTab(self.progress_tab, "Progress & Timeline")
        tabs.addTab(self.principles_tab, "TRIZ Principles")
        
        self.setCentralWidget(tabs)
        
        # Connect project selection signal
        self.project_tab.project_selected.connect(self.on_project_selected)
        
        self.show()
    
    def on_project_selected(self, project_id):
        """Handle project selection"""
        self.problem_tab.set_current_project(project_id)
        self.contradiction_tab.set_current_project(project_id)
        self.resource_tab.set_current_project(project_id)
        self.design_tab.set_current_project(project_id)
        self.progress_tab.set_current_project(project_id)


def main():
    app = QApplication(sys.argv)
    dashboard = TRIZDashboard()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
