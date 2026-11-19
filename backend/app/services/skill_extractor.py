import re
from typing import Dict, List, Set, Tuple, Any

# Canonical skill taxonomy: category -> list of canonical names
SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Dart",
        "Shell Scripting", "Bash", "PowerShell", "Objective-C", "Haskell", "Clojure",
        "Elixir", "Erlang", "Lua", "Julia", "Groovy", "Fortran", "Cobol", "Assembly",
        "Solidity", "VHDL", "Verilog", "F#", "Visual Basic", "SQL", "PL/SQL", "T-SQL",
        "SAS", "Apex", "VBA"
    ],
    "Web Frameworks & Libraries": [
        "React", "Angular", "Vue.js", "Next.js", "Nuxt.js", "Django", "Flask",
        "FastAPI", "Express.js", "Spring Boot", "Ruby on Rails", "ASP.NET", "ASP.NET Core",
        "Laravel", "Symfony", "Svelte", "jQuery", "HTML5", "CSS3", "Tailwind CSS",
        "Bootstrap", "Material-UI", "Redux", "MobX", "Zustand", "GraphQL", "REST APIs",
        "WebSockets", "gRPC", "Node.js", "NestJS", "Gatsby", "Vite", "Webpack",
        "Babel", "Electron", "Sass", "Less", "Chakra UI", "Alpine.js", "Blazor",
        "Sinatra", "Fastify", "Koa", "Celery", "Socket.io", "Remix"
    ],
    "Databases & Storage": [
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Elasticsearch",
        "Apache Cassandra", "DynamoDB", "Oracle Database", "Microsoft SQL Server",
        "Neo4j", "Couchbase", "MariaDB", "Snowflake", "Google BigQuery", "Amazon Redshift",
        "ClickHouse", "Apache HBase", "Supabase", "Firebase", "Realm", "Milvus",
        "Pinecone", "ChromaDB", "Faiss", "Weaviate", "Memcached", "Firestore", "CockroachDB"
    ],
    "Cloud & DevOps": [
        "Amazon Web Services (AWS)", "AWS", "Microsoft Azure", "Google Cloud Platform (GCP)",
        "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "CI/CD",
        "GitHub Actions", "GitLab CI", "Helm", "OpenShift", "Vagrant", "Nomad",
        "Consul", "Apache Kafka", "RabbitMQ", "ActiveMQ", "Nginx", "Apache HTTP Server",
        "Traefik", "Linux", "Ubuntu", "Debian", "CentOS", "RedHat", "Prometheus",
        "Grafana", "ELK Stack", "Datadog", "New Relic", "Splunk", "ArgoCD", "CloudFormation",
        "Serverless", "AWS Lambda", "Azure Functions", "Google Cloud Run", "ECS", "EKS",
        "GKE", "S3", "EC2", "RDS", "IAM", "CloudFront", "Route53"
    ],
    "Data Science & AI/ML": [
        "TensorFlow", "PyTorch", "scikit-learn", "Keras", "Pandas", "NumPy", "SciPy",
        "Apache Spark", "Databricks", "Apache Hadoop", "Apache Flink", "Apache Airflow",
        "dbt", "Tableau", "Power BI", "Matplotlib", "Seaborn", "Plotly", "OpenCV",
        "NLTK", "spaCy", "Hugging Face", "Transformers", "LangChain", "LlamaIndex",
        "XGBoost", "LightGBM", "CatBoost", "Computer Vision", "Natural Language Processing (NLP)",
        "Deep Learning", "Machine Learning", "Reinforcement Learning", "MLOps", "MLflow",
        "Weights & Biases", "Data Modeling", "Data Warehousing", "ETL Pipelines",
        "Large Language Models (LLMs)", "Generative AI", "RAG", "Vector Embeddings",
        "BERT", "GPT", "Predictive Analytics", "Statistical Modeling", "A/B Testing"
    ],
    "Testing & Quality Assurance": [
        "Pytest", "JUnit", "Jest", "Mocha", "Chai", "Cypress", "Selenium",
        "Playwright", "Postman", "JMeter", "Locust", "SonarQube", "Cucumber",
        "TestNG", "Unit Testing", "Integration Testing", "End-to-End Testing",
        "Load Testing", "Performance Testing", "TDD", "BDD"
    ],
    "Tools & Methodologies": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Trello",
        "Asana", "Agile", "Scrum", "Kanban", "DevOps", "Microservices",
        "System Design", "Design Patterns", "Object-Oriented Programming (OOP)",
        "Functional Programming", "Clean Architecture", "Code Review", "VS Code",
        "PyCharm", "IntelliJ IDEA", "Postman", "Figma", "Swagger", "OpenAPI"
    ],
    "Security & Networking": [
        "Cybersecurity", "Network Security", "OAuth2", "OpenID Connect", "JWT",
        "SAML", "SSL/TLS", "Penetration Testing", "Vulnerability Assessment",
        "Firewalls", "VPN", "DNS", "TCP/IP", "HTTP/HTTPS", "Zero Trust",
        "OWASP", "Cryptography", "Identity and Access Management (IAM)", "SIEM"
    ],
    "Mobile Development": [
        "Android", "iOS", "React Native", "Flutter", "SwiftUI", "Jetpack Compose",
        "Kotlin Multiplatform", "Xamarin", "Ionic", "Cordova", "Mobile App Development"
    ],
    "Soft Skills & Leadership": [
        "Leadership", "Team Leadership", "Communication", "Teamwork", "Cross-Functional Collaboration",
        "Problem Solving", "Critical Thinking", "Analytical Thinking", "Mentoring",
        "Project Management", "Stakeholder Management", "Time Management", "Adaptability",
        "Negotiation", "Conflict Resolution", "Public Speaking", "Technical Writing"
    ]
}

# Alias / Synonym / Variations mapping to canonical skill name
SKILL_ALIASES: Dict[str, str] = {
    # Languages
    "py": "Python",
    "python3": "Python",
    "golang": "Go",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    ".net": "ASP.NET",
    "dotnet": "ASP.NET",
    "dotnet core": "ASP.NET Core",
    ".net core": "ASP.NET Core",
    "sh": "Shell Scripting",
    "bash": "Bash",
    "shell": "Shell Scripting",
    "zsh": "Shell Scripting",
    "powershell": "PowerShell",
    
    # Web & Frontend
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react native": "React Native",
    "angular": "Angular",
    "angularjs": "Angular",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nuxt": "Nuxt.js",
    "nuxtjs": "Nuxt.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    "ror": "Ruby on Rails",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "mui": "Material-UI",
    "material ui": "Material-UI",
    "graphql": "GraphQL",
    "rest": "REST APIs",
    "restful": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",

    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "my sql": "MySQL",
    "mysql": "MySQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    "redis": "Redis",
    "elastic": "Elasticsearch",
    "elasticsearch": "Elasticsearch",
    "cassandra": "Apache Cassandra",
    "dynamodb": "DynamoDB",
    "dynamo db": "DynamoDB",
    "mssql": "Microsoft SQL Server",
    "sql server": "Microsoft SQL Server",
    "bigquery": "Google BigQuery",
    "redshift": "Amazon Redshift",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform (GCP)",
    "google cloud": "Google Cloud Platform (GCP)",
    "k8s": "Kubernetes",
    "kube": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "tf": "Terraform",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "gh actions": "GitHub Actions",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "kafka": "Apache Kafka",
    "apache kafka": "Apache Kafka",
    "rabbitmq": "RabbitMQ",
    "rabbit mq": "RabbitMQ",
    "nginx": "Nginx",
    "ci cd": "CI/CD",
    "ci/cd": "CI/CD",
    "continuous integration": "CI/CD",
    "lambda": "AWS Lambda",
    "aws lambda": "AWS Lambda",

    # AI & ML
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "torch": "PyTorch",
    "pytorch": "PyTorch",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "spark": "Apache Spark",
    "pyspark": "Apache Spark",
    "airflow": "Apache Airflow",
    "nlp": "Natural Language Processing (NLP)",
    "natural language processing": "Natural Language Processing (NLP)",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "llm": "Large Language Models (LLMs)",
    "llms": "Large Language Models (LLMs)",
    "rag": "RAG",
    "retrieval augmented generation": "RAG",
    "langchain": "LangChain",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",

    # Tools
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "jira": "Jira",
    "confluence": "Confluence",
    "agile": "Agile",
    "scrum": "Scrum",
    "kanban": "Kanban",
    "microservices": "Microservices",
    "system design": "System Design",
    "oop": "Object-Oriented Programming (OOP)",
    "unit testing": "Unit Testing",
    "pytest": "Pytest",
    "selenium": "Selenium",
    "jest": "Jest",
    "postman": "Postman"
}


class SkillExtractor:
    """Extracts, normalizes, categorizes, and deduplicates skills from text."""

    def __init__(self):
        # Build lookup table: normalized_key -> canonical_name, category
        self.skill_map: Dict[str, Tuple[str, str]] = {}

        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                normalized = skill.lower()
                self.skill_map[normalized] = (skill, category)

        # Add aliases
        for alias, canonical in SKILL_ALIASES.items():
            normalized_alias = alias.lower()
            category = self._lookup_category(canonical)
            self.skill_map[normalized_alias] = (canonical, category)

        # Precompile regex patterns for matching
        # Sort keys by length descending to match longest phrases first (e.g., "React Native" before "React")
        self.sorted_keys = sorted(self.skill_map.keys(), key=lambda x: len(x), reverse=True)

    def _lookup_category(self, canonical_name: str) -> str:
        for cat, skills in SKILL_TAXONOMY.items():
            if canonical_name in skills:
                return cat
        return "Technical"

    def normalize_skill_name(self, name: str) -> str:
        """Map raw skill string or alias to canonical skill name."""
        clean = name.strip()
        lower = clean.lower()
        if lower in self.skill_map:
            return self.skill_map[lower][0]
        # Return title-cased or trimmed name if not in dictionary
        return clean

    def normalize_skill(self, name: str):
        """Return tuple of (canonical_name, category) for a given skill or alias."""
        canonical = self.normalize_skill_name(name)
        category = self.get_skill_category(canonical)
        return canonical, category

    def get_skill_category(self, name: str) -> str:
        """Get skill category for canonical or raw skill name."""
        lower = name.strip().lower()
        if lower in self.skill_map:
            return self.skill_map[lower][1]
        return "Technical"

    def extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract all recognized skills from arbitrary text.
        Returns a list of structured skill dictionaries:
            [{ "name": "Python", "category": "Programming Languages", "normalized": "python" }, ...]
        """
        if not text:
            return []

        found_skills: Dict[str, Dict[str, Any]] = {}
        text_lower = f" {text.lower()} "

        # Replace common separators with spaces for boundary matching
        cleaned_text = re.sub(r"[,;/\(\)\[\]\{\}\*•·\-_]", " ", text_lower)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text)

        # 1. Match multi-word and punctuation-sensitive skills with exact regex
        for key in self.sorted_keys:
            canonical, category = self.skill_map[key]

            # Short skills (<= 2 chars like C, R, Go, CI, CD, JS, TS) require strict word boundaries
            if len(key) <= 2:
                # Require boundary or slash
                escaped = re.escape(key)
                pattern = rf"(?:^|[\s,;/()|]){escaped}(?:$|[\s,;/()|])"
                if re.search(pattern, text_lower):
                    if canonical not in found_skills:
                        found_skills[canonical] = {
                            "name": canonical,
                            "category": category,
                            "normalized": canonical.lower(),
                        }
            else:
                # Use standard boundary matching
                escaped = re.escape(key)
                pattern = rf"\b{escaped}\b"
                if re.search(pattern, text_lower) or re.search(pattern, cleaned_text):
                    if canonical not in found_skills:
                        found_skills[canonical] = {
                            "name": canonical,
                            "category": category,
                            "normalized": canonical.lower(),
                        }

        # Return sorted by category, then name
        return sorted(found_skills.values(), key=lambda x: (x["category"], x["name"]))

    def categorize_skills(self, skill_names: List[str]) -> Dict[str, List[str]]:
        """Group a list of skill names by category."""
        categorized: Dict[str, List[str]] = {}
        for s in skill_names:
            norm = self.normalize_skill_name(s)
            cat = self.get_skill_category(norm)
            if cat not in categorized:
                categorized[cat] = []
            if norm not in categorized[cat]:
                categorized[cat].append(norm)
        return categorized


# Singleton instance for application-wide use
skill_extractor = SkillExtractor()
