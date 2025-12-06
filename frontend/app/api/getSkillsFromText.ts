import baseUrl from './baseUrl';
import type { Skill } from '~/types';

interface GetSkillsFromTextResponse {
    skills: Skill[];
    confidence: number;
}

// Comprehensive skill taxonomy with keywords and aliases
const SKILL_TAXONOMY: Record<string, { keywords: string[]; category: string }> = {
    // Programming Languages
    'Python': { keywords: ['python', 'py', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'scipy', 'matplotlib', 'jupyter', 'pip', 'conda', 'anaconda', 'pytorch', 'tensorflow'], category: 'language' },
    'JavaScript': { keywords: ['javascript', 'js', 'es6', 'es2015', 'ecmascript', 'node', 'nodejs', 'npm', 'yarn', 'pnpm', 'vanilla js'], category: 'language' },
    'TypeScript': { keywords: ['typescript', 'ts', 'tsc', 'typed javascript', 'type-safe'], category: 'language' },
    'Java': { keywords: ['java', 'jvm', 'jdk', 'jre', 'spring', 'springboot', 'maven', 'gradle', 'hibernate', 'jdbc', 'servlet', 'jsp', 'tomcat'], category: 'language' },
    'C++': { keywords: ['c++', 'cpp', 'cplusplus', 'stl', 'boost', 'qt', 'cmake', 'makefile'], category: 'language' },
    'C': { keywords: ['c programming', 'c language', 'ansi c', 'gcc', 'clang', 'pointer', 'malloc'], category: 'language' },
    'C#': { keywords: ['c#', 'csharp', 'c sharp', '.net', 'dotnet', 'asp.net', 'unity', 'xamarin', 'blazor', 'wpf', 'winforms'], category: 'language' },
    'Go': { keywords: ['golang', 'go lang', 'go programming', 'goroutine', 'gopher'], category: 'language' },
    'Rust': { keywords: ['rust', 'rustlang', 'cargo', 'rustc', 'ownership', 'borrowing'], category: 'language' },
    'Ruby': { keywords: ['ruby', 'rails', 'ruby on rails', 'ror', 'gem', 'bundler', 'sinatra'], category: 'language' },
    'PHP': { keywords: ['php', 'laravel', 'symfony', 'wordpress', 'drupal', 'composer', 'artisan'], category: 'language' },
    'Swift': { keywords: ['swift', 'swiftui', 'ios development', 'xcode', 'cocoa', 'uikit'], category: 'language' },
    'Kotlin': { keywords: ['kotlin', 'android development', 'jetpack', 'coroutines'], category: 'language' },
    'Scala': { keywords: ['scala', 'akka', 'play framework', 'sbt', 'spark scala'], category: 'language' },
    'R': { keywords: ['r programming', 'r language', 'rstudio', 'ggplot', 'tidyverse', 'dplyr', 'cran'], category: 'language' },
    'MATLAB': { keywords: ['matlab', 'simulink', 'octave', 'matrix laboratory'], category: 'language' },
    'Perl': { keywords: ['perl', 'cpan', 'regex perl'], category: 'language' },
    'Haskell': { keywords: ['haskell', 'ghc', 'cabal', 'functional programming', 'monads'], category: 'language' },
    'Elixir': { keywords: ['elixir', 'phoenix', 'erlang', 'beam', 'otp'], category: 'language' },
    'Clojure': { keywords: ['clojure', 'clojurescript', 'lisp', 'leiningen'], category: 'language' },
    'Dart': { keywords: ['dart', 'flutter', 'dartlang'], category: 'language' },
    'Lua': { keywords: ['lua', 'luajit', 'love2d', 'neovim lua'], category: 'language' },
    'Julia': { keywords: ['julia', 'julialang', 'scientific computing'], category: 'language' },
    'Assembly': { keywords: ['assembly', 'asm', 'x86', 'arm', 'mips', 'nasm', 'low-level'], category: 'language' },
    'Shell': { keywords: ['bash', 'shell', 'zsh', 'sh', 'powershell', 'batch', 'scripting', 'terminal', 'cli'], category: 'language' },
    'SQL': { keywords: ['sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'oracle', 'mssql', 'tsql', 'plsql', 'query', 'database query'], category: 'language' },

    // Frontend Frameworks & Libraries
    'React': { keywords: ['react', 'reactjs', 'react.js', 'jsx', 'hooks', 'redux', 'context api', 'react native', 'nextjs', 'next.js', 'gatsby', 'remix'], category: 'frontend' },
    'Vue.js': { keywords: ['vue', 'vuejs', 'vue.js', 'vuex', 'pinia', 'nuxt', 'nuxtjs', 'composition api'], category: 'frontend' },
    'Angular': { keywords: ['angular', 'angularjs', 'rxjs', 'ngrx', 'angular material'], category: 'frontend' },
    'Svelte': { keywords: ['svelte', 'sveltekit', 'svelte kit'], category: 'frontend' },
    'HTML': { keywords: ['html', 'html5', 'semantic html', 'markup', 'dom', 'web page'], category: 'frontend' },
    'CSS': { keywords: ['css', 'css3', 'flexbox', 'grid', 'responsive', 'media queries', 'animations', 'transitions', 'stylesheet'], category: 'frontend' },
    'Sass': { keywords: ['sass', 'scss', 'less', 'stylus', 'css preprocessor'], category: 'frontend' },
    'Tailwind CSS': { keywords: ['tailwind', 'tailwindcss', 'utility-first', 'utility css'], category: 'frontend' },
    'Bootstrap': { keywords: ['bootstrap', 'bootstrap5', 'responsive framework'], category: 'frontend' },
    'Material UI': { keywords: ['material ui', 'mui', 'material design', 'chakra ui', 'ant design', 'antd'], category: 'frontend' },
    'jQuery': { keywords: ['jquery', 'ajax', 'dom manipulation'], category: 'frontend' },
    'WebGL': { keywords: ['webgl', 'three.js', 'threejs', 'webgpu', '3d graphics', 'canvas', 'pixi'], category: 'frontend' },
    'D3.js': { keywords: ['d3', 'd3.js', 'data visualization', 'svg charts', 'interactive charts'], category: 'frontend' },

    // Backend Frameworks
    'Node.js': { keywords: ['node', 'nodejs', 'node.js', 'express', 'expressjs', 'koa', 'fastify', 'nestjs', 'hapi'], category: 'backend' },
    'Django': { keywords: ['django', 'drf', 'django rest framework', 'python web'], category: 'backend' },
    'Flask': { keywords: ['flask', 'werkzeug', 'jinja', 'flask api'], category: 'backend' },
    'FastAPI': { keywords: ['fastapi', 'starlette', 'pydantic', 'async python'], category: 'backend' },
    'Spring Boot': { keywords: ['spring', 'springboot', 'spring boot', 'spring mvc', 'spring security', 'spring data'], category: 'backend' },
    'ASP.NET': { keywords: ['asp.net', 'aspnet', 'asp.net core', 'web api', 'razor', 'entity framework'], category: 'backend' },
    'Ruby on Rails': { keywords: ['rails', 'ruby on rails', 'ror', 'activerecord', 'action cable'], category: 'backend' },
    'Laravel': { keywords: ['laravel', 'eloquent', 'blade', 'artisan', 'php framework'], category: 'backend' },
    'GraphQL': { keywords: ['graphql', 'apollo', 'relay', 'hasura', 'prisma graphql', 'schema'], category: 'backend' },
    'REST API': { keywords: ['rest', 'restful', 'api', 'api design', 'openapi', 'swagger', 'postman', 'endpoints'], category: 'backend' },
    'gRPC': { keywords: ['grpc', 'protobuf', 'protocol buffers', 'rpc'], category: 'backend' },
    'WebSockets': { keywords: ['websocket', 'websockets', 'socket.io', 'real-time', 'ws'], category: 'backend' },

    // Databases
    'PostgreSQL': { keywords: ['postgresql', 'postgres', 'psql', 'pg', 'relational database'], category: 'database' },
    'MySQL': { keywords: ['mysql', 'mariadb', 'percona'], category: 'database' },
    'MongoDB': { keywords: ['mongodb', 'mongo', 'mongoose', 'nosql', 'document database', 'bson'], category: 'database' },
    'Redis': { keywords: ['redis', 'cache', 'in-memory', 'key-value', 'caching'], category: 'database' },
    'Elasticsearch': { keywords: ['elasticsearch', 'elastic', 'elk', 'kibana', 'logstash', 'full-text search'], category: 'database' },
    'Cassandra': { keywords: ['cassandra', 'apache cassandra', 'distributed database', 'wide-column'], category: 'database' },
    'DynamoDB': { keywords: ['dynamodb', 'dynamo', 'aws database'], category: 'database' },
    'Firebase': { keywords: ['firebase', 'firestore', 'realtime database', 'firebase auth'], category: 'database' },
    'Neo4j': { keywords: ['neo4j', 'graph database', 'cypher', 'knowledge graph'], category: 'database' },
    'SQLite': { keywords: ['sqlite', 'sqlite3', 'embedded database', 'local database'], category: 'database' },
    'Oracle': { keywords: ['oracle', 'oracle db', 'plsql', 'oracle database'], category: 'database' },
    'SQL Server': { keywords: ['sql server', 'mssql', 'tsql', 'microsoft sql'], category: 'database' },

    // Cloud & DevOps
    'AWS': { keywords: ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'cloudformation', 'sqs', 'sns', 'rds', 'ecs', 'eks', 'fargate', 'cloudwatch', 'iam', 'vpc', 'route53', 'api gateway'], category: 'cloud' },
    'Azure': { keywords: ['azure', 'microsoft azure', 'azure devops', 'azure functions', 'azure storage', 'cosmos db', 'aks'], category: 'cloud' },
    'Google Cloud': { keywords: ['gcp', 'google cloud', 'bigquery', 'cloud run', 'gke', 'cloud functions', 'pub/sub', 'dataflow'], category: 'cloud' },
    'Docker': { keywords: ['docker', 'dockerfile', 'container', 'containerization', 'docker-compose', 'docker compose', 'docker hub', 'image', 'container image'], category: 'devops' },
    'Kubernetes': { keywords: ['kubernetes', 'k8s', 'kubectl', 'helm', 'pods', 'deployment', 'service mesh', 'istio', 'container orchestration'], category: 'devops' },
    'Terraform': { keywords: ['terraform', 'infrastructure as code', 'iac', 'hcl', 'terragrunt', 'tfstate'], category: 'devops' },
    'Ansible': { keywords: ['ansible', 'playbook', 'configuration management', 'automation'], category: 'devops' },
    'Jenkins': { keywords: ['jenkins', 'ci/cd', 'pipeline', 'continuous integration', 'build automation'], category: 'devops' },
    'GitHub Actions': { keywords: ['github actions', 'workflows', 'gh actions', 'github ci'], category: 'devops' },
    'GitLab CI': { keywords: ['gitlab ci', 'gitlab', 'gitlab pipeline', 'gitlab runner'], category: 'devops' },
    'CI/CD': { keywords: ['ci/cd', 'cicd', 'continuous integration', 'continuous deployment', 'continuous delivery', 'devops pipeline'], category: 'devops' },
    'Linux': { keywords: ['linux', 'ubuntu', 'debian', 'centos', 'fedora', 'rhel', 'unix', 'sysadmin', 'system administration'], category: 'devops' },
    'Nginx': { keywords: ['nginx', 'reverse proxy', 'load balancer', 'web server'], category: 'devops' },
    'Apache': { keywords: ['apache', 'httpd', 'apache server'], category: 'devops' },
    'Monitoring': { keywords: ['prometheus', 'grafana', 'datadog', 'new relic', 'monitoring', 'observability', 'metrics', 'alerting'], category: 'devops' },

    // Machine Learning & AI
    'Machine Learning': { keywords: ['machine learning', 'ml', 'supervised learning', 'unsupervised learning', 'regression', 'classification', 'clustering', 'feature engineering'], category: 'ml' },
    'Deep Learning': { keywords: ['deep learning', 'neural network', 'neural networks', 'cnn', 'rnn', 'lstm', 'transformer', 'attention', 'backpropagation'], category: 'ml' },
    'TensorFlow': { keywords: ['tensorflow', 'tf', 'keras', 'tf.keras', 'tensorboard'], category: 'ml' },
    'PyTorch': { keywords: ['pytorch', 'torch', 'torchvision', 'lightning'], category: 'ml' },
    'Scikit-learn': { keywords: ['scikit-learn', 'sklearn', 'scikit', 'machine learning python'], category: 'ml' },
    'Natural Language Processing': { keywords: ['nlp', 'natural language', 'text processing', 'tokenization', 'named entity', 'ner', 'sentiment analysis', 'text classification', 'spacy', 'nltk', 'huggingface', 'transformers', 'bert', 'gpt', 'llm', 'large language model'], category: 'ml' },
    'Computer Vision': { keywords: ['computer vision', 'cv', 'image processing', 'object detection', 'image classification', 'opencv', 'yolo', 'image recognition', 'face detection', 'ocr'], category: 'ml' },
    'Data Science': { keywords: ['data science', 'data analysis', 'data analytics', 'exploratory data', 'eda', 'statistical analysis', 'statistics'], category: 'ml' },
    'Pandas': { keywords: ['pandas', 'dataframe', 'data manipulation', 'data wrangling'], category: 'ml' },
    'NumPy': { keywords: ['numpy', 'numerical computing', 'arrays', 'matrix operations'], category: 'ml' },
    'MLOps': { keywords: ['mlops', 'ml pipeline', 'model deployment', 'mlflow', 'kubeflow', 'model serving'], category: 'ml' },
    'Reinforcement Learning': { keywords: ['reinforcement learning', 'rl', 'q-learning', 'policy gradient', 'gym', 'agent'], category: 'ml' },

    // Data Engineering
    'Apache Spark': { keywords: ['spark', 'pyspark', 'spark sql', 'databricks', 'distributed computing'], category: 'data' },
    'Apache Kafka': { keywords: ['kafka', 'event streaming', 'message queue', 'pub-sub', 'kafka streams'], category: 'data' },
    'Airflow': { keywords: ['airflow', 'apache airflow', 'dag', 'workflow orchestration', 'etl'], category: 'data' },
    'ETL': { keywords: ['etl', 'data pipeline', 'data ingestion', 'data transformation', 'data loading'], category: 'data' },
    'Data Warehousing': { keywords: ['data warehouse', 'dwh', 'snowflake', 'redshift', 'bigquery', 'olap', 'dimensional modeling'], category: 'data' },
    'Hadoop': { keywords: ['hadoop', 'hdfs', 'mapreduce', 'hive', 'pig', 'yarn'], category: 'data' },
    'dbt': { keywords: ['dbt', 'data build tool', 'analytics engineering', 'data modeling'], category: 'data' },

    // Version Control & Collaboration
    'Git': { keywords: ['git', 'version control', 'github', 'gitlab', 'bitbucket', 'commit', 'branch', 'merge', 'pull request', 'pr', 'repository', 'repo', 'gitflow'], category: 'tools' },
    'Agile': { keywords: ['agile', 'scrum', 'kanban', 'sprint', 'user story', 'backlog', 'standup', 'retrospective', 'jira', 'trello'], category: 'methodology' },

    // Testing
    'Unit Testing': { keywords: ['unit test', 'unit testing', 'jest', 'mocha', 'chai', 'pytest', 'junit', 'xunit', 'nunit', 'test driven', 'tdd'], category: 'testing' },
    'Integration Testing': { keywords: ['integration test', 'integration testing', 'api testing', 'end-to-end', 'e2e', 'cypress', 'playwright', 'selenium', 'webdriver'], category: 'testing' },
    'Test Automation': { keywords: ['test automation', 'automated testing', 'qa automation', 'testing framework'], category: 'testing' },

    // Security
    'Cybersecurity': { keywords: ['security', 'cybersecurity', 'infosec', 'penetration testing', 'pentest', 'vulnerability', 'owasp', 'security audit'], category: 'security' },
    'Authentication': { keywords: ['authentication', 'authorization', 'oauth', 'oauth2', 'jwt', 'saml', 'sso', 'identity', 'auth0', 'keycloak'], category: 'security' },
    'Cryptography': { keywords: ['cryptography', 'encryption', 'hashing', 'ssl', 'tls', 'https', 'certificates', 'pki'], category: 'security' },

    // Mobile Development
    'iOS Development': { keywords: ['ios', 'iphone', 'ipad', 'swiftui', 'uikit', 'core data', 'app store'], category: 'mobile' },
    'Android Development': { keywords: ['android', 'android studio', 'kotlin android', 'java android', 'play store', 'jetpack compose'], category: 'mobile' },
    'React Native': { keywords: ['react native', 'expo', 'cross-platform mobile'], category: 'mobile' },
    'Flutter': { keywords: ['flutter', 'dart mobile', 'cross-platform'], category: 'mobile' },

    // Architecture & Design
    'System Design': { keywords: ['system design', 'architecture', 'scalability', 'high availability', 'distributed systems', 'microservices', 'monolith', 'soa'], category: 'architecture' },
    'Microservices': { keywords: ['microservices', 'micro services', 'service oriented', 'api gateway', 'service mesh'], category: 'architecture' },
    'Design Patterns': { keywords: ['design patterns', 'solid', 'dry', 'kiss', 'factory', 'singleton', 'observer', 'mvc', 'mvvm', 'clean architecture'], category: 'architecture' },
    'Object-Oriented Programming': { keywords: ['oop', 'object oriented', 'object-oriented', 'inheritance', 'polymorphism', 'encapsulation', 'abstraction', 'class', 'interface'], category: 'paradigm' },
    'Functional Programming': { keywords: ['functional programming', 'fp', 'immutability', 'pure functions', 'higher-order functions', 'lambda', 'map reduce filter'], category: 'paradigm' },

    // Game Development
    'Game Development': { keywords: ['game development', 'game dev', 'gamedev', 'unity', 'unreal', 'godot', 'game engine'], category: 'gamedev' },
    'Unity': { keywords: ['unity', 'unity3d', 'c# game', 'game engine unity'], category: 'gamedev' },
    'Unreal Engine': { keywords: ['unreal', 'unreal engine', 'ue4', 'ue5', 'blueprint'], category: 'gamedev' },

    // Blockchain
    'Blockchain': { keywords: ['blockchain', 'cryptocurrency', 'crypto', 'web3', 'decentralized', 'dapp', 'smart contract'], category: 'blockchain' },
    'Solidity': { keywords: ['solidity', 'ethereum', 'smart contracts', 'evm', 'hardhat', 'truffle'], category: 'blockchain' },

    // Embedded & IoT
    'Embedded Systems': { keywords: ['embedded', 'embedded systems', 'firmware', 'rtos', 'microcontroller', 'arduino', 'raspberry pi', 'esp32', 'stm32'], category: 'embedded' },
    'IoT': { keywords: ['iot', 'internet of things', 'mqtt', 'sensors', 'actuators', 'edge computing'], category: 'embedded' },

    // Other Skills
    'Problem Solving': { keywords: ['problem solving', 'algorithms', 'data structures', 'leetcode', 'competitive programming', 'optimization'], category: 'fundamental' },
    'Algorithms': { keywords: ['algorithm', 'algorithms', 'sorting', 'searching', 'dynamic programming', 'graph algorithms', 'big o', 'complexity'], category: 'fundamental' },
    'Data Structures': { keywords: ['data structure', 'data structures', 'array', 'linked list', 'tree', 'binary tree', 'hash table', 'stack', 'queue', 'heap', 'graph'], category: 'fundamental' },
    'APIs': { keywords: ['api', 'api design', 'api integration', 'third-party api', 'web services'], category: 'fundamental' },
    'Debugging': { keywords: ['debugging', 'troubleshooting', 'bug fixing', 'debugger', 'breakpoint', 'stack trace'], category: 'fundamental' },
    'Code Review': { keywords: ['code review', 'peer review', 'code quality', 'best practices', 'clean code'], category: 'fundamental' },
    'Documentation': { keywords: ['documentation', 'technical writing', 'readme', 'api docs', 'jsdoc', 'docstring'], category: 'fundamental' },
    'Performance Optimization': { keywords: ['performance', 'optimization', 'profiling', 'bottleneck', 'caching', 'lazy loading', 'code optimization'], category: 'fundamental' },
    'Accessibility': { keywords: ['accessibility', 'a11y', 'wcag', 'screen reader', 'aria', 'inclusive design'], category: 'frontend' },
    'SEO': { keywords: ['seo', 'search engine optimization', 'meta tags', 'structured data', 'core web vitals'], category: 'frontend' },
    'WebAssembly': { keywords: ['webassembly', 'wasm', 'assemblyscript'], category: 'frontend' },
    'PWA': { keywords: ['pwa', 'progressive web app', 'service worker', 'offline first', 'manifest'], category: 'frontend' },
};

interface SkillMatch {
    skill: string;
    matches: string[];
    score: number;
    category: string;
}

function extractSkillsFromText(text: string): { skills: Skill[]; confidence: number } {
    const normalizedText = text.toLowerCase();
    const words = normalizedText.split(/\s+/);
    const skillMatches: Map<string, SkillMatch> = new Map();

    // Count word frequencies for context
    const wordFrequency: Map<string, number> = new Map();
    words.forEach(word => {
        const cleanWord = word.replace(/[^a-z0-9+#.]/g, '');
        if (cleanWord.length > 1) {
            wordFrequency.set(cleanWord, (wordFrequency.get(cleanWord) || 0) + 1);
        }
    });

    // Check each skill against the text
    for (const [skill, { keywords, category }] of Object.entries(SKILL_TAXONOMY)) {
        const matchedKeywords: string[] = [];
        let totalScore = 0;

        for (const keyword of keywords) {
            // Handle multi-word keywords
            if (keyword.includes(' ')) {
                const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
                const matches = normalizedText.match(regex);
                if (matches) {
                    matchedKeywords.push(keyword);
                    totalScore += matches.length * 2; // Multi-word matches are more valuable
                }
            } else {
                // Single word keyword
                const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
                const matches = normalizedText.match(regex);
                if (matches) {
                    matchedKeywords.push(keyword);
                    totalScore += matches.length;
                }
            }
        }

        if (matchedKeywords.length > 0) {
            skillMatches.set(skill, {
                skill,
                matches: matchedKeywords,
                score: totalScore,
                category,
            });
        }
    }

    // Convert to skills array with normalized values
    const maxScore = Math.max(...Array.from(skillMatches.values()).map(m => m.score), 1);
    
    const skills: Skill[] = Array.from(skillMatches.values())
        .map(match => ({
            name: match.skill,
            // Normalize score: minimum 0.2 for any detected skill, max 1.0
            // Use logarithmic scaling for better distribution
            value: Math.round((0.2 + 0.8 * (Math.log(match.score + 1) / Math.log(maxScore + 1))) * 100),
        }))
        .sort((a, b) => b.value - a.value);

    // Calculate confidence based on text quality and matches
    const textLength = text.length;
    const matchCount = skills.length;
    const avgScore = skills.length > 0 ? skills.reduce((a, b) => a + b.value, 0) / skills.length : 0;
    
    // Confidence factors:
    // - More text = more confidence (up to a point)
    // - More skills found = more confidence
    // - Higher average scores = more confidence
    const lengthFactor = Math.min(textLength / 1000, 1);
    const matchFactor = Math.min(matchCount / 10, 1);
    const scoreFactor = avgScore / 100;
    
    const confidence = Math.round((0.3 * lengthFactor + 0.4 * matchFactor + 0.3 * scoreFactor) * 100) / 100;

    return { skills, confidence: Math.min(confidence, 0.95) };
}

export async function getSkillsFromText(text: string): Promise<GetSkillsFromTextResponse> {
    // First try to use the backend API if available
    try {
        const response = await fetch(`${baseUrl}/skills/extract`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });
        
        if (response.ok) {
            return response.json();
        }
    } catch {
        // Backend not available, fall through to local extraction
    }

    // Use local skill extraction as fallback
    return extractSkillsFromText(text);
}