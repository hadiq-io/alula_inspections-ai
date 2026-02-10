"""
Schema Registry - Database Schema Discovery and Semantic Layer
==============================================================
Automatically discovers database schema and provides semantic annotations
for AI-powered dynamic query generation. The heart of the intelligent system.

Features:
- Automatic table/column discovery
- Semantic annotations (column meanings, business concepts)
- Join path discovery between tables
- Data type inference
- Query complexity estimation
- Performance hints

Author: AlUla Inspection AI
Version: 2.0
"""

import os
import pyodbc
import json
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from functools import lru_cache
import threading
import hashlib


@dataclass
class ColumnInfo:
    """Column metadata with semantic annotations."""
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_table: Optional[str] = None
    foreign_column: Optional[str] = None
    
    # Semantic annotations
    semantic_type: Optional[str] = None  # e.g., "date", "count", "money", "identifier"
    business_concept: Optional[str] = None  # e.g., "inspection_date", "violation_count"
    description: Optional[str] = None
    sample_values: List[str] = field(default_factory=list)
    
    # Query hints
    is_indexed: bool = False
    cardinality: Optional[int] = None  # Approximate distinct values
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TableInfo:
    """Table metadata with relationships."""
    name: str
    schema: str = "dbo"
    row_count: int = 0
    columns: Dict[str, ColumnInfo] = field(default_factory=dict)
    primary_keys: List[str] = field(default_factory=list)
    
    # Semantic annotations
    business_domain: Optional[str] = None  # e.g., "inspections", "violations", "locations"
    description: Optional[str] = None
    is_ml_table: bool = False
    is_core_table: bool = False
    
    # Relationships
    outgoing_relations: List[Dict] = field(default_factory=list)  # This table references others
    incoming_relations: List[Dict] = field(default_factory=list)  # Other tables reference this
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "schema": self.schema,
            "row_count": self.row_count,
            "columns": {k: v.to_dict() for k, v in self.columns.items()},
            "primary_keys": self.primary_keys,
            "business_domain": self.business_domain,
            "description": self.description,
            "is_ml_table": self.is_ml_table,
            "is_core_table": self.is_core_table,
            "outgoing_relations": self.outgoing_relations,
            "incoming_relations": self.incoming_relations
        }


@dataclass
class JoinPath:
    """Represents a join path between two tables."""
    from_table: str
    to_table: str
    join_columns: List[Tuple[str, str]]  # [(from_col, to_col), ...]
    join_type: str = "INNER"
    cost: int = 1  # Lower is better
    
    def to_sql(self) -> str:
        """Generate SQL JOIN clause."""
        conditions = " AND ".join([
            f"{self.from_table}.{fc} = {self.to_table}.{tc}"
            for fc, tc in self.join_columns
        ])
        return f"{self.join_type} JOIN {self.to_table} ON {conditions}"


class SemanticAnnotations:
    """
    Semantic layer mapping business concepts to database columns.
    This is the intelligence that allows the AI to understand what columns mean.
    """
    
    # Business concept to column mappings
    CONCEPT_MAPPINGS = {
        # Inspection concepts
        "inspection": {
            "tables": ["Event"],
            "count_column": "Id",
            "date_column": "SubmitionDate",
            "keywords": ["inspection", "event", "visit", "تفتيش", "زيارة", "فحص"]
        },
        "inspection_score": {
            "tables": ["Event"],
            "value_column": "Score",
            "keywords": ["score", "rating", "compliance", "نتيجة", "تقييم", "امتثال"]
        },
        "inspection_status": {
            "tables": ["Event"],
            "value_column": "Status",
            "keywords": ["status", "state", "حالة", "وضع"]
        },
        
        # Violation concepts
        "violation": {
            "tables": ["EventViolation"],
            "count_column": "Id",
            "keywords": ["violation", "issue", "problem", "مخالفة", "مشكلة"]
        },
        "violation_value": {
            "tables": ["EventViolation"],
            "value_column": "ViolationValue",
            "keywords": ["value", "fine", "amount", "penalty", "قيمة", "غرامة", "مبلغ"]
        },
        "violation_severity": {
            "tables": ["EventViolation"],
            "value_column": "Severity",
            "keywords": ["severity", "critical", "major", "minor", "شدة", "خطورة"]
        },
        "objection": {
            "tables": ["EventViolation"],
            "value_column": "HasObjection",
            "status_column": "ObjectionStatus",
            "keywords": ["objection", "appeal", "اعتراض", "استئناف"]
        },
        
        # Location concepts
        "location": {
            "tables": ["Locations"],
            "name_column": "Name",
            "name_ar_column": "NameAr",
            "id_column": "Id",
            "keywords": ["location", "place", "site", "venue", "موقع", "مكان"]
        },
        "neighborhood": {
            "tables": ["Locations"],
            "name_column": "Name",
            "keywords": ["neighborhood", "area", "district", "حي", "منطقة"]
        },
        
        # Business type concepts
        "activity": {
            "tables": ["LocationType"],
            "name_column": "Name",
            "name_ar_column": "NameAr",
            "keywords": ["activity", "business", "type", "restaurant", "bakery", "نشاط", "مطعم", "مخبز"]
        },
        
        # Time concepts
        "date": {
            "keywords": ["date", "when", "year", "month", "day", "تاريخ", "سنة", "شهر"]
        },
        "period": {
            "keywords": ["period", "quarter", "week", "فترة", "ربع"]
        },
        
        # People concepts
        "inspector": {
            "tables": ["Event"],
            "id_column": "ReporterID",
            "keywords": ["inspector", "reporter", "officer", "مفتش", "مراقب"]
        },
        
        # ML concepts
        "risk": {
            "tables": ["ML_Location_Risk"],
            "value_column": "risk_probability",
            "category_column": "risk_category",
            "keywords": ["risk", "danger", "threat", "خطر", "تهديد"]
        },
        "prediction": {
            "tables": ["ML_Predictions"],
            "value_column": "predicted_value",
            "keywords": ["prediction", "forecast", "تنبؤ", "توقع"]
        },
        "anomaly": {
            "tables": ["ML_Anomalies"],
            "value_column": "anomaly_probability",
            "keywords": ["anomaly", "unusual", "outlier", "شاذ", "غير عادي"]
        },
        "performance": {
            "tables": ["ML_Inspector_Performance"],
            "value_column": "performance_score",
            "keywords": ["performance", "efficiency", "أداء", "كفاءة"]
        },
        
        # Health Certificate concepts (NEW - what client asked for!)
        "health_certificate": {
            "tables": ["Locations", "Event"],
            "keywords": ["health certificate", "certificate", "license", "permit", 
                        "شهادة صحية", "شهادة", "رخصة", "تصريح"],
            "related_columns": ["LicenseId", "HealthCertificateNumber", "CertificateExpiry",
                               "LicenseNumber", "LicenseExpiry", "PermitNumber"]
        }
    }
    
    # Column name patterns for automatic type detection
    COLUMN_PATTERNS = {
        r".*_?id$": "identifier",
        r".*_?date.*|.*_?at$|created|modified|submition": "datetime",
        r".*count.*|.*num.*|total.*": "count",
        r".*value.*|.*amount.*|.*price.*|.*cost.*": "money",
        r".*score.*|.*rate.*|.*percent.*": "percentage",
        r".*name.*": "name",
        r".*_?ar$|.*arabic.*": "arabic_text",
        r".*_?en$|.*english.*": "english_text",
        r"is_?.*|has_?.*": "boolean",
        r".*status.*|.*state.*": "status",
        r".*type.*|.*category.*|.*level.*": "category",
        r".*description.*|.*note.*|.*comment.*": "text",
        r".*probability.*|.*likelihood.*": "probability",
        r".*duration.*|.*time.*|.*minutes.*|.*hours.*": "duration"
    }
    
    @classmethod
    def get_concept_for_keywords(cls, text: str) -> List[str]:
        """Find business concepts that match keywords in text."""
        text_lower = text.lower()
        matches = []
        
        for concept, info in cls.CONCEPT_MAPPINGS.items():
            for keyword in info.get("keywords", []):
                if keyword.lower() in text_lower:
                    matches.append(concept)
                    break
        
        return list(set(matches))
    
    @classmethod
    def infer_column_type(cls, column_name: str) -> Optional[str]:
        """Infer semantic type from column name."""
        col_lower = column_name.lower()
        
        for pattern, sem_type in cls.COLUMN_PATTERNS.items():
            if re.match(pattern, col_lower, re.IGNORECASE):
                return sem_type
        
        return None
    
    @classmethod
    def get_tables_for_concept(cls, concept: str) -> List[str]:
        """Get tables associated with a business concept."""
        if concept in cls.CONCEPT_MAPPINGS:
            return cls.CONCEPT_MAPPINGS[concept].get("tables", [])
        return []


class SchemaRegistry:
    """
    Central registry for database schema with intelligent caching and semantic layer.
    
    This is the brain of the dynamic query system - it knows everything about the database
    and can guide the AI to generate correct SQL.
    """
    
    # Tables to prioritize for inspection domain
    CORE_TABLES = [
        "Event", "EventViolation", "Locations", "LocationType", "EventType"
    ]
    
    # ML tables
    ML_TABLES = [
        "ML_Predictions", "ML_Location_Risk", "ML_Inspector_Performance",
        "ML_Anomalies", "ML_Severity_Predictions", "ML_Objection_Predictions",
        "ML_Recurrence_Predictions", "ML_Location_Clusters", "ML_Scheduling_Recommendations"
    ]
    
    # Tables to skip (system tables, etc.)
    SKIP_TABLES = [
        "sysdiagrams", "__EFMigrationsHistory", "AspNet.*"
    ]
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize schema registry."""
        self._tables: Dict[str, TableInfo] = {}
        self._join_paths: Dict[str, List[JoinPath]] = {}
        self._last_refresh: Optional[datetime] = None
        self._lock = threading.Lock()
        self._connection_string = connection_string or self._build_connection_string()
        self._semantic = SemanticAnnotations()
        self._concept_index: Dict[str, Set[str]] = {}  # concept -> set of table.column
        
    def _build_connection_string(self) -> str:
        """Build connection string from environment."""
        db_server = os.getenv("DB_SERVER", "20.3.236.169")
        db_port = os.getenv("DB_PORT", "1433")
        db_name = os.getenv("DB_NAME", "CHECK_ELM_AlUlaRC_DW")
        db_user = os.getenv("DB_USERNAME", "sa")
        db_password = os.getenv("DB_PASSWORD", "StrongPass123!")
        
        return (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={db_server},{db_port};"
            f"DATABASE={db_name};"
            f"UID={db_user};"
            f"PWD={db_password};"
            f"TrustServerCertificate=yes;"
        )
    
    def initialize(self, force_refresh: bool = False) -> bool:
        """
        Initialize the schema registry by discovering database schema.
        
        Args:
            force_refresh: Force refresh even if recently updated
            
        Returns:
            True if successful
        """
        # Check if refresh needed (cached for 1 hour)
        if not force_refresh and self._last_refresh:
            if datetime.now() - self._last_refresh < timedelta(hours=1):
                return True
        
        try:
            with self._lock:
                conn = pyodbc.connect(self._connection_string, timeout=30)
                cursor = conn.cursor()
                
                # Step 1: Discover all tables
                self._discover_tables(cursor)
                
                # Step 2: Discover columns for each table
                self._discover_columns(cursor)
                
                # Step 3: Discover primary keys
                self._discover_primary_keys(cursor)
                
                # Step 4: Discover foreign key relationships
                self._discover_foreign_keys(cursor)
                
                # Step 5: Get row counts for core tables
                self._discover_row_counts(cursor)
                
                # Step 6: Build join paths
                self._build_join_paths()
                
                # Step 7: Apply semantic annotations
                self._apply_semantic_annotations()
                
                # Step 8: Build concept index
                self._build_concept_index()
                
                cursor.close()
                conn.close()
                
                self._last_refresh = datetime.now()
                print(f"✅ Schema registry initialized: {len(self._tables)} tables discovered")
                return True
                
        except Exception as e:
            print(f"❌ Schema registry initialization error: {e}")
            return False
    
    def _discover_tables(self, cursor) -> None:
        """Discover all tables in the database."""
        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        for row in cursor.fetchall():
            schema, name = row
            
            # Skip system tables
            skip = False
            for pattern in self.SKIP_TABLES:
                if re.match(pattern, name, re.IGNORECASE):
                    skip = True
                    break
            
            if skip:
                continue
            
            table = TableInfo(
                name=name,
                schema=schema,
                is_core_table=name in self.CORE_TABLES,
                is_ml_table=name in self.ML_TABLES or name.startswith("ML_")
            )
            
            # Assign business domain
            if name in self.CORE_TABLES:
                if "Event" in name and "Violation" not in name:
                    table.business_domain = "inspections"
                elif "Violation" in name:
                    table.business_domain = "violations"
                elif "Location" in name:
                    table.business_domain = "locations"
            elif table.is_ml_table:
                table.business_domain = "ml_predictions"
            
            self._tables[name] = table
    
    def _discover_columns(self, cursor) -> None:
        """Discover columns for all tables."""
        cursor.execute("""
            SELECT 
                TABLE_NAME, 
                COLUMN_NAME, 
                DATA_TYPE,
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE
            FROM INFORMATION_SCHEMA.COLUMNS
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """)
        
        for row in cursor.fetchall():
            table_name = row[0]
            if table_name not in self._tables:
                continue
            
            col = ColumnInfo(
                name=row[1],
                data_type=row[2],
                is_nullable=(row[3] == "YES"),
                semantic_type=self._semantic.infer_column_type(row[1])
            )
            
            self._tables[table_name].columns[row[1]] = col
    
    def _discover_primary_keys(self, cursor) -> None:
        """Discover primary keys for all tables."""
        cursor.execute("""
            SELECT 
                tc.TABLE_NAME,
                kcu.COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu 
                ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
        """)
        
        for row in cursor.fetchall():
            table_name, col_name = row
            if table_name in self._tables:
                self._tables[table_name].primary_keys.append(col_name)
                if col_name in self._tables[table_name].columns:
                    self._tables[table_name].columns[col_name].is_primary_key = True
    
    def _discover_foreign_keys(self, cursor) -> None:
        """Discover foreign key relationships."""
        cursor.execute("""
            SELECT 
                fk.name AS FK_Name,
                tp.name AS Parent_Table,
                cp.name AS Parent_Column,
                tr.name AS Referenced_Table,
                cr.name AS Referenced_Column
            FROM sys.foreign_keys fk
            INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
            INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
            INNER JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
            INNER JOIN sys.columns cp ON fkc.parent_column_id = cp.column_id 
                AND fkc.parent_object_id = cp.object_id
            INNER JOIN sys.columns cr ON fkc.referenced_column_id = cr.column_id 
                AND fkc.referenced_object_id = cr.object_id
        """)
        
        for row in cursor.fetchall():
            fk_name, parent_table, parent_col, ref_table, ref_col = row
            
            if parent_table in self._tables:
                self._tables[parent_table].outgoing_relations.append({
                    "to_table": ref_table,
                    "from_column": parent_col,
                    "to_column": ref_col
                })
                
                if parent_col in self._tables[parent_table].columns:
                    col = self._tables[parent_table].columns[parent_col]
                    col.is_foreign_key = True
                    col.foreign_table = ref_table
                    col.foreign_column = ref_col
            
            if ref_table in self._tables:
                self._tables[ref_table].incoming_relations.append({
                    "from_table": parent_table,
                    "from_column": parent_col,
                    "to_column": ref_col
                })
    
    def _discover_row_counts(self, cursor) -> None:
        """Get approximate row counts for tables."""
        # Use system view for fast approximate counts
        cursor.execute("""
            SELECT 
                t.name AS TableName,
                p.rows AS RowCount
            FROM sys.tables t
            INNER JOIN sys.partitions p ON t.object_id = p.object_id
            WHERE p.index_id IN (0, 1)  -- heap or clustered index
        """)
        
        for row in cursor.fetchall():
            table_name, count = row
            if table_name in self._tables:
                self._tables[table_name].row_count = count or 0
    
    def _build_join_paths(self) -> None:
        """Build join paths between tables based on foreign keys."""
        for table_name, table in self._tables.items():
            for rel in table.outgoing_relations:
                path_key = f"{table_name}->{rel['to_table']}"
                
                join_path = JoinPath(
                    from_table=table_name,
                    to_table=rel['to_table'],
                    join_columns=[(rel['from_column'], rel['to_column'])],
                    join_type="INNER",
                    cost=1
                )
                
                if path_key not in self._join_paths:
                    self._join_paths[path_key] = []
                self._join_paths[path_key].append(join_path)
        
        # Add commonly used joins that might not have explicit FK
        common_joins = [
            ("EventViolation", "Event", "EventId", "Id"),
            ("Event", "Locations", "Location", "Id"),
            ("Locations", "LocationType", "LocationType", "Id"),
            ("ML_Location_Risk", "Locations", "location_id", "Id"),
            ("ML_Anomalies", "Event", "inspection_id", "Id"),
        ]
        
        for from_t, to_t, from_c, to_c in common_joins:
            path_key = f"{from_t}->{to_t}"
            if path_key not in self._join_paths:
                self._join_paths[path_key] = [JoinPath(
                    from_table=from_t,
                    to_table=to_t,
                    join_columns=[(from_c, to_c)],
                    join_type="LEFT",
                    cost=1
                )]
    
    def _apply_semantic_annotations(self) -> None:
        """Apply business semantic annotations to columns."""
        # Map concepts to specific columns
        annotations = {
            "Event": {
                "Id": ("identifier", "Unique inspection ID"),
                "SubmitionDate": ("datetime", "Date and time of inspection submission"),
                "Status": ("status", "Inspection status (0=Open, 1=Closed)"),
                "Score": ("percentage", "Compliance score (0-100)"),
                "Duration": ("duration", "Inspection duration in minutes"),
                "ReporterID": ("identifier", "Inspector/reporter ID"),
                "Location": ("identifier", "Location ID being inspected"),
                "IssueCount": ("count", "Total issues found"),
                "CriticalIssueCount": ("count", "Critical issues found"),
                "EventType": ("identifier", "Type of inspection event"),
                "IsDeleted": ("boolean", "Soft delete flag"),
                "LicenseId": ("identifier", "Associated business license/certificate ID")
            },
            "EventViolation": {
                "Id": ("identifier", "Unique violation ID"),
                "EventId": ("identifier", "Parent inspection ID"),
                "ViolationValue": ("money", "Monetary value of violation/fine"),
                "Severity": ("category", "Violation severity level"),
                "HasObjection": ("boolean", "Whether objection was filed"),
                "ObjectionStatus": ("status", "Status of objection if filed"),
                "QuestionNameEn": ("english_text", "Violation description in English"),
                "QuestionNameAr": ("arabic_text", "Violation description in Arabic")
            },
            "Locations": {
                "Id": ("identifier", "Unique location ID"),
                "Name": ("name", "Location name in English"),
                "NameAr": ("arabic_text", "Location name in Arabic"),
                "LocationType": ("identifier", "Business type ID"),
                "Isdeleted": ("boolean", "Soft delete flag")
            },
            "LocationType": {
                "Id": ("identifier", "Unique business type ID"),
                "Name": ("name", "Business type in English"),
                "NameAr": ("arabic_text", "Business type in Arabic"),
                "IsDeleted": ("boolean", "Soft delete flag")
            }
        }
        
        for table_name, columns in annotations.items():
            if table_name in self._tables:
                for col_name, (sem_type, desc) in columns.items():
                    if col_name in self._tables[table_name].columns:
                        col = self._tables[table_name].columns[col_name]
                        col.semantic_type = sem_type
                        col.description = desc
    
    def _build_concept_index(self) -> None:
        """Build an index from business concepts to table.column references."""
        for concept, info in SemanticAnnotations.CONCEPT_MAPPINGS.items():
            self._concept_index[concept] = set()
            
            tables = info.get("tables", [])
            for table in tables:
                if table in self._tables:
                    # Add specific columns mentioned in the concept
                    for key in ["count_column", "value_column", "id_column", 
                                "name_column", "date_column", "category_column",
                                "status_column", "name_ar_column"]:
                        if key in info:
                            self._concept_index[concept].add(f"{table}.{info[key]}")
                    
                    # Add related columns
                    for col in info.get("related_columns", []):
                        if col in self._tables[table].columns:
                            self._concept_index[concept].add(f"{table}.{col}")
    
    # ============== PUBLIC API ==============
    
    def get_table(self, table_name: str) -> Optional[TableInfo]:
        """Get table info by name."""
        return self._tables.get(table_name)
    
    def get_all_tables(self) -> Dict[str, TableInfo]:
        """Get all tables."""
        return self._tables.copy()
    
    def get_core_tables(self) -> List[TableInfo]:
        """Get only core business tables."""
        return [t for t in self._tables.values() if t.is_core_table]
    
    def get_ml_tables(self) -> List[TableInfo]:
        """Get ML prediction tables."""
        return [t for t in self._tables.values() if t.is_ml_table]
    
    def get_tables_for_concept(self, concept: str) -> List[str]:
        """Get tables relevant to a business concept."""
        return SemanticAnnotations.get_tables_for_concept(concept)
    
    def get_columns_for_concept(self, concept: str) -> Set[str]:
        """Get table.column references for a concept."""
        return self._concept_index.get(concept, set())
    
    def find_join_path(self, from_table: str, to_table: str) -> Optional[JoinPath]:
        """Find the best join path between two tables."""
        path_key = f"{from_table}->{to_table}"
        if path_key in self._join_paths and self._join_paths[path_key]:
            return self._join_paths[path_key][0]  # Return best (first) path
        
        # Try reverse
        reverse_key = f"{to_table}->{from_table}"
        if reverse_key in self._join_paths and self._join_paths[reverse_key]:
            # Reverse the join
            original = self._join_paths[reverse_key][0]
            return JoinPath(
                from_table=to_table,
                to_table=from_table,
                join_columns=[(tc, fc) for fc, tc in original.join_columns],
                join_type=original.join_type,
                cost=original.cost
            )
        
        return None
    
    def get_schema_context_for_ai(self, concepts: List[str] = None, 
                                   include_all_core: bool = True) -> str:
        """
        Generate a schema context string for AI prompting.
        This is what gets injected into Claude's context for dynamic SQL generation.
        """
        lines = ["# Database Schema Context\n"]
        
        # Determine which tables to include
        tables_to_include = set()
        
        if concepts:
            for concept in concepts:
                for table in self.get_tables_for_concept(concept):
                    tables_to_include.add(table)
        
        if include_all_core or not tables_to_include:
            tables_to_include.update(self.CORE_TABLES)
        
        # Include ML tables if relevant concepts
        ml_concepts = {"risk", "prediction", "anomaly", "performance", "forecast"}
        if concepts and ml_concepts.intersection(set(concepts)):
            tables_to_include.update(self.ML_TABLES[:5])  # Add top 5 ML tables
        
        # Generate schema descriptions
        for table_name in sorted(tables_to_include):
            if table_name not in self._tables:
                continue
            
            table = self._tables[table_name]
            lines.append(f"\n## Table: {table_name}")
            if table.description:
                lines.append(f"Description: {table.description}")
            if table.business_domain:
                lines.append(f"Domain: {table.business_domain}")
            lines.append(f"Rows: ~{table.row_count:,}")
            
            lines.append("\n### Columns:")
            for col_name, col in table.columns.items():
                type_str = col.data_type
                extras = []
                if col.is_primary_key:
                    extras.append("PK")
                if col.is_foreign_key:
                    extras.append(f"FK→{col.foreign_table}")
                if col.semantic_type:
                    extras.append(col.semantic_type)
                
                extra_str = f" [{', '.join(extras)}]" if extras else ""
                desc_str = f" -- {col.description}" if col.description else ""
                lines.append(f"  - {col_name}: {type_str}{extra_str}{desc_str}")
        
        # Add join information
        lines.append("\n## Common Joins:")
        for path_key, paths in self._join_paths.items():
            if paths:
                path = paths[0]
                if path.from_table in tables_to_include or path.to_table in tables_to_include:
                    joins = ", ".join([f"{fc}={tc}" for fc, tc in path.join_columns])
                    lines.append(f"  - {path.from_table} → {path.to_table} ON {joins}")
        
        # Add important notes
        lines.append("\n## Important Notes:")
        lines.append("  - Use IsDeleted = 0 for Event and Locations tables")
        lines.append("  - Date column for inspections: Event.SubmitionDate")
        lines.append("  - Status 0 = Open, 1 = Closed for Event.Status")
        lines.append("  - Score is compliance percentage (0-100)")
        lines.append("  - Arabic columns end with 'Ar' (e.g., NameAr, QuestionNameAr)")
        
        return "\n".join(lines)
    
    def search_columns(self, search_term: str) -> List[Tuple[str, str, ColumnInfo]]:
        """
        Search for columns matching a term.
        Returns list of (table_name, column_name, column_info).
        """
        results = []
        search_lower = search_term.lower()
        
        for table_name, table in self._tables.items():
            for col_name, col in table.columns.items():
                # Check column name
                if search_lower in col_name.lower():
                    results.append((table_name, col_name, col))
                    continue
                
                # Check description
                if col.description and search_lower in col.description.lower():
                    results.append((table_name, col_name, col))
                    continue
                
                # Check semantic type
                if col.semantic_type and search_lower in col.semantic_type.lower():
                    results.append((table_name, col_name, col))
        
        return results
    
    def suggest_tables_for_query(self, query_text: str) -> List[str]:
        """
        Suggest relevant tables based on a natural language query.
        Uses semantic concept matching.
        """
        concepts = SemanticAnnotations.get_concept_for_keywords(query_text)
        
        suggested = set()
        for concept in concepts:
            suggested.update(self.get_tables_for_concept(concept))
        
        # Always include Event as the central table for most queries
        if not suggested or any(c in concepts for c in ["inspection", "violation", "location"]):
            suggested.add("Event")
        
        return list(suggested)
    
    def validate_sql_tables(self, tables: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that SQL uses only known tables.
        Returns (is_valid, list of invalid table names).
        """
        invalid = [t for t in tables if t not in self._tables]
        return len(invalid) == 0, invalid
    
    def validate_sql_columns(self, table: str, columns: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that columns exist in a table.
        Returns (is_valid, list of invalid column names).
        """
        if table not in self._tables:
            return False, columns
        
        valid_columns = set(self._tables[table].columns.keys())
        invalid = [c for c in columns if c not in valid_columns]
        return len(invalid) == 0, invalid
    
    def stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_tables": len(self._tables),
            "core_tables": len([t for t in self._tables.values() if t.is_core_table]),
            "ml_tables": len([t for t in self._tables.values() if t.is_ml_table]),
            "total_columns": sum(len(t.columns) for t in self._tables.values()),
            "join_paths": len(self._join_paths),
            "concepts_indexed": len(self._concept_index),
            "last_refresh": self._last_refresh.isoformat() if self._last_refresh else None
        }
    
    def export_schema(self) -> Dict[str, Any]:
        """Export complete schema as dictionary (for caching/debugging)."""
        return {
            "tables": {name: table.to_dict() for name, table in self._tables.items()},
            "join_paths": {k: [asdict(p) for p in v] for k, v in self._join_paths.items()},
            "stats": self.stats()
        }


# Global singleton instance
_schema_registry: Optional[SchemaRegistry] = None
_registry_lock = threading.Lock()


def get_schema_registry() -> SchemaRegistry:
    """Get the global schema registry instance (singleton)."""
    global _schema_registry
    
    with _registry_lock:
        if _schema_registry is None:
            _schema_registry = SchemaRegistry()
            _schema_registry.initialize()
        return _schema_registry


def refresh_schema_registry() -> bool:
    """Force refresh the global schema registry."""
    global _schema_registry
    
    with _registry_lock:
        if _schema_registry is None:
            _schema_registry = SchemaRegistry()
        return _schema_registry.initialize(force_refresh=True)
