"""Synthetic content for the evaluation corpus.

Every company, figure and table here is fictional and chosen by hand so the eval
has exact ground truth. Chart/table numbers are intentionally kept OUT of the
prose and captions, so they only exist inside the rendered images.
"""

DOCS = [
    {
        "file": "aurora-retail-annual-report-2025.pdf",
        "title": "Aurora Retail Group — Annual Report 2025",
        "paragraphs": [
            "Aurora Retail Group is an omnichannel specialty retailer headquartered "
            "in Denver, Colorado. Founded in 2009, the company operates neighbourhood "
            "stores alongside a fast-growing online marketplace, and is known for its "
            "loyalty programme and same-day fulfilment network.",
            "Fiscal year 2025 was a year of disciplined expansion. Management focused "
            "on higher-margin private-label lines and on deepening engagement with "
            "loyalty members, while holding new-store openings to dense urban corridors.",
        ],
        "facts": [
            {"q": "In which city is Aurora Retail Group headquartered?", "a": "Denver", "type": "text"},
            {"q": "In what year was Aurora Retail Group founded?", "a": "2009", "type": "numeric", "value": 2009},
        ],
        "bar": {
            "title": "Revenue by Quarter (USD millions), FY2025",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [182, 205, 197, 243],
            "metric": "quarterly revenue",
            "unit": "USD millions",
            "caption": "Revenue rose across the year, with the strongest quarter driven "
            "by the holiday season and private-label growth.",
        },
        "line": {
            "title": "Active Loyalty Members (millions), 2021–2025",
            "labels": ["2021", "2022", "2023", "2024", "2025"],
            "values": [3.1, 3.8, 4.6, 5.9, 7.2],
            "metric": "the number of active loyalty members",
            "unit": "million",
            "caption": "Loyalty membership compounded steadily as same-day fulfilment "
            "expanded into new metros.",
        },
        "table": {
            "title": "Store Footprint by Region (2025)",
            "cols": ["Region", "Stores", "Avg. size (sq ft)"],
            "rows": [
                ["West", "128", "24,500"],
                ["Midwest", "94", "21,000"],
                ["South", "141", "26,800"],
                ["Northeast", "77", "19,400"],
            ],
            "questions": [
                {"q": "How many stores does Aurora operate in the South region?", "a": "141", "type": "numeric", "value": 141},
                {"q": "What is the average store size in the West region (sq ft)?", "a": "24,500", "type": "numeric", "value": 24500},
                {"q": "Which region has the fewest stores?", "a": "Northeast", "type": "choice"},
            ],
            "caption": "The footprint remains concentrated in high-density corridors, "
            "with regional formats tuned to local demand.",
        },
        "unanswerable": [
            "What is Aurora Retail Group's net carbon emissions target for 2030?",
        ],
    },
    {
        "file": "nimbus-cloud-q4-metrics-2025.pdf",
        "title": "Nimbus Cloud — Q4 Platform Metrics 2025",
        "paragraphs": [
            "Nimbus Cloud provides a managed data-streaming platform for engineering "
            "teams. The company is based in Austin, Texas, and serves customers across "
            "financial services, gaming and logistics.",
            "This quarterly update summarises platform usage and reliability. The "
            "engineering organisation prioritised ingestion throughput and reducing "
            "cold-start latency for serverless connectors.",
        ],
        "facts": [
            {"q": "In which city is Nimbus Cloud based?", "a": "Austin", "type": "text"},
            {"q": "Which industries does Nimbus Cloud serve?", "a": "financial services, gaming and logistics", "type": "text"},
        ],
        "bar": {
            "title": "Monthly Events Processed (billions), Q4",
            "labels": ["Oct", "Nov", "Dec"],
            "values": [41, 47, 58],
            "metric": "the number of events processed",
            "unit": "billion",
            "caption": "Event volume climbed through the quarter as new logistics "
            "customers onboarded ahead of peak season.",
        },
        "line": {
            "title": "Median API Latency (ms), by Week",
            "labels": ["W1", "W2", "W3", "W4", "W5"],
            "values": [88, 76, 71, 63, 59],
            "metric": "median API latency",
            "unit": "ms",
            "caption": "Latency improved week over week following the connector "
            "cold-start optimisation.",
        },
        "table": {
            "title": "Reliability by Service Tier (Q4)",
            "cols": ["Tier", "Uptime (%)", "Incidents"],
            "rows": [
                ["Enterprise", "99.98", "1"],
                ["Business", "99.94", "3"],
                ["Developer", "99.90", "6"],
            ],
            "questions": [
                {"q": "How many incidents occurred on the Business tier in Q4?", "a": "3", "type": "numeric", "value": 3},
                {"q": "What uptime percentage did the Enterprise tier achieve?", "a": "99.98", "type": "numeric", "value": 99.98},
                {"q": "Which service tier had the most incidents?", "a": "Developer", "type": "choice"},
            ],
            "caption": "Higher tiers benefited from isolated capacity and priority "
            "failover during the peak period.",
        },
        "unanswerable": [
            "What is the annual subscription price of the Nimbus Cloud Enterprise tier?",
        ],
    },
    {
        "file": "helios-energy-solar-datasheet-2025.pdf",
        "title": "Helios Energy — SunCore 480 Solar Panel Datasheet 2025",
        "paragraphs": [
            "The Helios SunCore 480 is a monocrystalline solar panel designed for "
            "commercial rooftop installations. Helios Energy is headquartered in "
            "Fremont, California, and manufactures modules with a 25-year warranty.",
            "This datasheet lists measured electrical and thermal characteristics. "
            "Values were captured under standard test conditions unless noted otherwise.",
        ],
        "facts": [
            {"q": "Where is Helios Energy headquartered?", "a": "Fremont", "type": "text"},
            {"q": "How long is the SunCore 480 warranty, in years?", "a": "25", "type": "numeric", "value": 25},
        ],
        "bar": {
            "title": "Rated Power Output by Model (watts)",
            "labels": ["320", "400", "480", "560"],
            "values": [320, 400, 480, 560],
            "metric": "rated power output",
            "unit": "watts",
            "caption": "The product line spans entry to high-output modules for varied "
            "roof areas.",
        },
        "line": {
            "title": "Efficiency vs. Cell Temperature (%)",
            "labels": ["15C", "25C", "35C", "45C", "55C"],
            "values": [21.8, 21.2, 20.5, 19.7, 18.8],
            "metric": "module efficiency",
            "unit": "percent",
            "caption": "Efficiency declines gradually as cell temperature rises, "
            "consistent with the module's temperature coefficient.",
        },
        "table": {
            "title": "Electrical Characteristics (SunCore 480)",
            "cols": ["Parameter", "Value", "Unit"],
            "rows": [
                ["Open-circuit voltage", "49.6", "V"],
                ["Short-circuit current", "11.8", "A"],
                ["Max power voltage", "41.2", "V"],
                ["Max power current", "11.2", "A"],
            ],
            "questions": [
                {"q": "What is the open-circuit voltage of the SunCore 480, in volts?", "a": "49.6", "type": "numeric", "value": 49.6},
                {"q": "What is the short-circuit current of the SunCore 480, in amps?", "a": "11.8", "type": "numeric", "value": 11.8},
            ],
            "caption": "Characteristics are specified at standard test conditions of "
            "1000 W/m2 and 25C cell temperature.",
        },
        "unanswerable": [
            "What is the shipping weight of a pallet of SunCore 480 panels?",
            "Which distributor stocks the SunCore 480 in Germany?",
        ],
    },
    {
        "file": "meridian-biolabs-research-summary-2025.pdf",
        "title": "Meridian BioLabs — Assay Research Summary 2025",
        "paragraphs": [
            "Meridian BioLabs develops diagnostic assays for clinical laboratories. "
            "The organisation operates from Boston, Massachusetts, and this summary "
            "reports internal validation results for its rapid-panel programme.",
            "All measurements are from controlled bench studies. Figures describe assay "
            "sensitivity and turnaround performance across sample batches.",
        ],
        "facts": [
            {"q": "From which city does Meridian BioLabs operate?", "a": "Boston", "type": "text"},
            {"q": "What programme does the summary report on?", "a": "rapid-panel", "type": "text"},
        ],
        "bar": {
            "title": "Assay Sensitivity by Panel (%)",
            "labels": ["Panel A", "Panel B", "Panel C", "Panel D"],
            "values": [94, 88, 97, 91],
            "metric": "assay sensitivity",
            "unit": "percent",
            "caption": "Sensitivity varied by panel design, with the highest result "
            "from the redesigned reagent mix.",
        },
        "line": {
            "title": "Mean Turnaround Time by Batch (minutes)",
            "labels": ["B1", "B2", "B3", "B4"],
            "values": [46, 42, 39, 33],
            "metric": "mean turnaround time",
            "unit": "minutes",
            "caption": "Turnaround improved across batches as the automated liquid "
            "handling step was tuned.",
        },
        "table": {
            "title": "Validation Cohort Summary",
            "cols": ["Panel", "Samples", "False positives"],
            "rows": [
                ["Panel A", "1,200", "14"],
                ["Panel B", "1,050", "31"],
                ["Panel C", "1,340", "9"],
                ["Panel D", "1,110", "22"],
            ],
            "questions": [
                {"q": "How many samples were tested for Panel C?", "a": "1,340", "type": "numeric", "value": 1340},
                {"q": "How many false positives did Panel B record?", "a": "31", "type": "numeric", "value": 31},
                {"q": "Which panel had the fewest false positives?", "a": "Panel C", "type": "choice"},
            ],
            "caption": "Cohorts were drawn from de-identified residual samples across "
            "three partner sites.",
        },
        "unanswerable": [
            "What regulatory clearance date is expected for Panel C?",
        ],
    },
    {
        "file": "vertex-mobility-investor-update-2025.pdf",
        "title": "Vertex Mobility — Investor Update 2025",
        "paragraphs": [
            "Vertex Mobility designs electric delivery vans for urban logistics fleets. "
            "The company is based in Portland, Oregon, and went public in 2023. This "
            "update covers deliveries, range performance and order backlog.",
            "Management reiterated its focus on manufacturing yield and on expanding the "
            "charging-partner network in target metros.",
        ],
        "facts": [
            {"q": "In which city is Vertex Mobility based?", "a": "Portland", "type": "text"},
            {"q": "In what year did Vertex Mobility go public?", "a": "2023", "type": "numeric", "value": 2023},
        ],
        "bar": {
            "title": "Vehicles Delivered by Quarter, 2025",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [1200, 1650, 1900, 2400],
            "metric": "vehicles delivered",
            "unit": "vehicles",
            "caption": "Deliveries accelerated through the year as the second assembly "
            "line reached full rate.",
        },
        "line": {
            "title": "Average Range per Charge (miles), by Model Year",
            "labels": ["2022", "2023", "2024", "2025"],
            "values": [140, 165, 188, 210],
            "metric": "average range per charge",
            "unit": "miles",
            "caption": "Range improved with each model year through battery and "
            "aerodynamic refinements.",
        },
        "table": {
            "title": "Order Backlog by Segment (2025)",
            "cols": ["Segment", "Units", "Avg. price (USD)"],
            "rows": [
                ["Parcel", "5,400", "48,000"],
                ["Grocery", "3,100", "52,000"],
                ["Municipal", "1,800", "61,000"],
            ],
            "questions": [
                {"q": "How many units are in the Parcel segment backlog?", "a": "5,400", "type": "numeric", "value": 5400},
                {"q": "What is the average price of a Municipal segment vehicle (USD)?", "a": "61,000", "type": "numeric", "value": 61000},
                {"q": "Which segment has the largest order backlog by units?", "a": "Parcel", "type": "choice"},
            ],
            "caption": "Backlog mix skews toward parcel fleets, with municipal orders "
            "carrying the highest average price.",
        },
        "unanswerable": [
            "What is Vertex Mobility's gross margin target for 2027?",
        ],
    },
    {
        "file": "cobalt-foods-sustainability-report-2025.pdf",
        "title": "Cobalt Foods — Sustainability Report 2025",
        "paragraphs": [
            "Cobalt Foods is a plant-based packaged-goods manufacturer headquartered in "
            "Minneapolis, Minnesota. This report summarises environmental performance "
            "across water use, packaging and emissions for the 2025 fiscal year.",
            "Targets are measured against a 2020 baseline. The company continued to shift "
            "toward recycled packaging and renewable process heat.",
        ],
        "facts": [
            {"q": "Where is Cobalt Foods headquartered?", "a": "Minneapolis", "type": "text"},
            {"q": "Against which baseline year are targets measured?", "a": "2020", "type": "numeric", "value": 2020},
        ],
        "bar": {
            "title": "Water Use Intensity by Plant (litres per unit)",
            "labels": ["Plant 1", "Plant 2", "Plant 3"],
            "values": [3.4, 2.9, 4.1],
            "metric": "water use intensity",
            "unit": "litres per unit",
            "caption": "Water intensity differs by plant age and product mix, with the "
            "newest facility performing best.",
        },
        "line": {
            "title": "Recycled Packaging Share (%), 2021–2025",
            "labels": ["2021", "2022", "2023", "2024", "2025"],
            "values": [38, 45, 54, 66, 74],
            "metric": "the recycled packaging share",
            "unit": "percent",
            "caption": "Recycled content rose steadily as suppliers were requalified.",
        },
        "table": {
            "title": "Scope Emissions Summary (tonnes CO2e)",
            "cols": ["Scope", "2024", "2025"],
            "rows": [
                ["Scope 1", "18,200", "16,400"],
                ["Scope 2", "24,900", "21,100"],
                ["Scope 3", "96,500", "91,800"],
            ],
            "questions": [
                {"q": "What were Cobalt Foods' Scope 2 emissions in 2025 (tonnes CO2e)?", "a": "21,100", "type": "numeric", "value": 21100},
                {"q": "What were Scope 1 emissions in 2024 (tonnes CO2e)?", "a": "18,200", "type": "numeric", "value": 18200},
                {"q": "Which scope had the highest emissions in 2025?", "a": "Scope 3", "type": "choice"},
            ],
            "caption": "Emissions fell across all scopes year over year, led by "
            "renewable electricity procurement.",
        },
        "unanswerable": [
            "What is Cobalt Foods' revenue for the 2025 fiscal year?",
        ],
    },
]
