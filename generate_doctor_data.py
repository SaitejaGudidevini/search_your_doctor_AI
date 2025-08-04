#!/usr/bin/env python3
"""
Doctor Data Generator for SmartDoctors Project
Generates synthetic doctor profiles with realistic data for RAG testing
"""

import json
import random
from faker import Faker
from datetime import datetime

# Initialize Faker
fake = Faker()

# Define comprehensive specialty and sub-specialty mappings
SPECIALTY_SUBSPECIALTY_MAP = {
    "Cardiology": [
        "Interventional Cardiology",
        "Electrophysiology",
        "Pediatric Cardiology",
        "Heart Failure and Transplantation",
        "Preventive Cardiology",
        "Nuclear Cardiology"
    ],
    "Neurosurgery": [
        "Spine Surgery",
        "Pediatric Neurosurgery",
        "Neuro-oncology",
        "Vascular Neurosurgery",
        "Functional Neurosurgery",
        "Skull Base Surgery"
    ],
    "Oncology": [
        "Medical Oncology",
        "Surgical Oncology",
        "Radiation Oncology",
        "Pediatric Oncology",
        "Gynecologic Oncology",
        "Hematologic Oncology"
    ],
    "Orthopedic Surgery": [
        "Sports Medicine",
        "Joint Replacement",
        "Spine Surgery",
        "Pediatric Orthopedics",
        "Hand Surgery",
        "Trauma Surgery"
    ],
    "Pediatrics": [
        "Neonatology",
        "Pediatric Emergency Medicine",
        "Pediatric Gastroenterology",
        "Pediatric Pulmonology",
        "Developmental Pediatrics",
        "Pediatric Endocrinology"
    ],
    "Gastroenterology": [
        "Hepatology",
        "Inflammatory Bowel Disease",
        "Therapeutic Endoscopy",
        "Pancreatic Diseases",
        "Motility Disorders",
        "Transplant Hepatology"
    ],
    "Urology": [
        "Urologic Oncology",
        "Pediatric Urology",
        "Male Infertility",
        "Female Urology",
        "Kidney Stone Disease",
        "Robotic Surgery"
    ],
    "Dermatology": [
        "Cosmetic Dermatology",
        "Mohs Surgery",
        "Pediatric Dermatology",
        "Immunodermatology",
        "Dermatopathology",
        "Laser Surgery"
    ],
    "Neurology": [
        "Stroke and Cerebrovascular Disease",
        "Epilepsy",
        "Movement Disorders",
        "Multiple Sclerosis",
        "Headache Medicine",
        "Neuromuscular Disease"
    ],
    "Obstetrics and Gynecology": [
        "Maternal-Fetal Medicine",
        "Reproductive Endocrinology",
        "Gynecologic Oncology",
        "Urogynecology",
        "Minimally Invasive Surgery",
        "Adolescent Gynecology"
    ]
}

# Define locations and their associated hospitals
HOSPITAL_BY_LOCATION = {
    "New York, NY": [
        "Mount Sinai Hospital",
        "NYU Langone Health",
        "Columbia University Medical Center",
        "Memorial Sloan Kettering Cancer Center",
        "Hospital for Special Surgery",
        "Weill Cornell Medical Center"
    ],
    "Los Angeles, CA": [
        "Cedars-Sinai Medical Center",
        "UCLA Medical Center",
        "Keck Hospital of USC",
        "Children's Hospital Los Angeles",
        "City of Hope National Medical Center"
    ],
    "Chicago, IL": [
        "Northwestern Memorial Hospital",
        "Rush University Medical Center",
        "University of Chicago Medical Center",
        "Loyola University Medical Center",
        "Advocate Christ Medical Center"
    ],
    "Houston, TX": [
        "MD Anderson Cancer Center",
        "Houston Methodist Hospital",
        "Texas Children's Hospital",
        "Memorial Hermann-Texas Medical Center",
        "Baylor St. Luke's Medical Center"
    ],
    "Boston, MA": [
        "Massachusetts General Hospital",
        "Brigham and Women's Hospital",
        "Boston Children's Hospital",
        "Dana-Farber Cancer Institute",
        "Beth Israel Deaconess Medical Center"
    ],
    "Philadelphia, PA": [
        "Hospital of the University of Pennsylvania",
        "Children's Hospital of Philadelphia",
        "Thomas Jefferson University Hospital",
        "Temple University Hospital",
        "Penn Presbyterian Medical Center"
    ],
    "Seattle, WA": [
        "University of Washington Medical Center",
        "Seattle Children's Hospital",
        "Virginia Mason Medical Center",
        "Swedish Medical Center",
        "Harborview Medical Center"
    ],
    "San Francisco, CA": [
        "UCSF Medical Center",
        "Stanford Health Care",
        "California Pacific Medical Center",
        "Zuckerberg San Francisco General Hospital",
        "Kaiser Permanente San Francisco"
    ],
    "Atlanta, GA": [
        "Emory University Hospital",
        "Children's Healthcare of Atlanta",
        "Grady Memorial Hospital",
        "Piedmont Atlanta Hospital",
        "Northside Hospital"
    ],
    "Miami, FL": [
        "Jackson Memorial Hospital",
        "University of Miami Hospital",
        "Baptist Hospital of Miami",
        "Mount Sinai Medical Center Miami",
        "Nicklaus Children's Hospital"
    ]
}

# Languages commonly spoken by doctors
LANGUAGES = [
    ["English"],
    ["English", "Spanish"],
    ["English", "Mandarin"],
    ["English", "Hindi"],
    ["English", "Arabic"],
    ["English", "French"],
    ["English", "Korean"],
    ["English", "Russian"],
    ["English", "Portuguese"],
    ["English", "Japanese"],
    ["English", "Spanish", "Portuguese"],
    ["English", "Hindi", "Punjabi"],
    ["English", "Mandarin", "Cantonese"]
]

# Critical surgery summaries by specialty
SURGERY_SUMMARIES = {
    "Cardiology": [
        "performed over 500 successful coronary artery bypass grafting (CABG) procedures with a 98% success rate, specializing in minimally invasive techniques",
        "completed 300+ transcatheter aortic valve replacements (TAVR) with exceptional outcomes in high-risk patients",
        "pioneered robotic-assisted mitral valve repair techniques with over 200 successful procedures",
        "led complex heart transplant surgeries with post-operative survival rates exceeding national averages",
        "performed 400+ percutaneous coronary interventions including complex bifurcation stenting",
        "specialized in pediatric congenital heart defect repairs with over 150 successful operations"
    ],
    "Neurosurgery": [
        "completed 600+ brain tumor resections using advanced neuronavigation and awake craniotomy techniques",
        "performed over 400 complex spine surgeries including minimally invasive lumbar fusions",
        "specialized in deep brain stimulation procedures for Parkinson's disease with 200+ successful implants",
        "pioneered endovascular treatment of cerebral aneurysms with over 300 procedures",
        "led pediatric neurosurgery team in 150+ cases of spina bifida and hydrocephalus corrections",
        "performed 250+ microvascular decompressions for trigeminal neuralgia with excellent outcomes"
    ],
    "Oncology": [
        "managed treatment protocols for over 1000 cancer patients with personalized chemotherapy regimens",
        "performed 300+ tumor resections with margin-negative results in 95% of cases",
        "led clinical trials for novel immunotherapy treatments with 40% response rates in advanced cancers",
        "specialized in stereotactic radiosurgery with 500+ treatments for brain and spine metastases",
        "performed 200+ complex hepatobiliary cancer surgeries including Whipple procedures",
        "pioneered combination therapy protocols achieving 80% remission rates in pediatric leukemia"
    ],
    "Orthopedic Surgery": [
        "performed over 800 total joint replacements including complex revision surgeries",
        "specialized in arthroscopic sports medicine procedures with 500+ ACL reconstructions",
        "completed 300+ complex spine surgeries including scoliosis corrections in pediatric patients",
        "pioneered minimally invasive hip replacement techniques with 400+ successful procedures",
        "performed 200+ complex trauma reconstructions including pelvic and acetabular fractures",
        "led hand surgery program with 600+ procedures including microsurgical nerve repairs"
    ],
    "Pediatrics": [
        "managed care for over 5000 pediatric patients including 200+ complex chronic disease cases",
        "specialized in neonatal intensive care with successful management of 300+ premature infants",
        "led pediatric emergency department handling 10,000+ annual visits with excellent outcomes",
        "performed 150+ pediatric bronchoscopies and advanced pulmonary procedures",
        "managed 400+ cases of pediatric diabetes with innovative continuous glucose monitoring protocols",
        "specialized in developmental disorders diagnosing and treating 500+ autism spectrum cases"
    ],
    "Gastroenterology": [
        "performed over 5000 colonoscopies with adenoma detection rate of 45%, well above national average",
        "completed 300+ ERCP procedures for complex biliary and pancreatic disorders",
        "specialized in liver transplant evaluation and post-transplant care for 200+ patients",
        "pioneered endoscopic submucosal dissection techniques with 150+ successful procedures",
        "managed 500+ inflammatory bowel disease patients with biologic therapy protocols",
        "performed 400+ therapeutic endoscopies including variceal banding and stricture dilations"
    ],
    "Urology": [
        "performed over 500 robotic-assisted prostatectomies with excellent continence outcomes",
        "completed 300+ kidney stone procedures including complex percutaneous nephrolithotomy",
        "specialized in pediatric urology with 200+ hypospadias repairs and reconstructive surgeries",
        "performed 400+ transurethral resections for bladder cancer with low recurrence rates",
        "led male infertility program with 150+ successful microsurgical varicocelectomies",
        "pioneered laser enucleation techniques for benign prostatic hyperplasia with 300+ procedures"
    ],
    "Dermatology": [
        "performed over 2000 Mohs micrographic surgeries with 99% cure rate for skin cancers",
        "completed 500+ complex reconstructions following skin cancer removal",
        "specialized in pediatric dermatology managing 300+ cases of severe atopic dermatitis",
        "performed 1000+ cosmetic procedures including laser resurfacing and injectable treatments",
        "led phototherapy program treating 400+ patients with psoriasis and vitiligo",
        "pioneered combination therapy approaches for 200+ melanoma patients"
    ],
    "Neurology": [
        "managed over 1000 stroke patients with rapid thrombolysis protocols improving outcomes by 40%",
        "specialized in epilepsy management with 300+ patients achieving seizure freedom",
        "led movement disorders clinic treating 500+ Parkinson's disease patients with DBS referrals",
        "performed 200+ botulinum toxin injections for dystonia and spasticity management",
        "managed 400+ multiple sclerosis patients with disease-modifying therapy protocols",
        "specialized in neuromuscular diseases diagnosing and treating 300+ rare disorder cases"
    ],
    "Obstetrics and Gynecology": [
        "delivered over 2000 babies including 300+ high-risk pregnancies with excellent outcomes",
        "performed 500+ minimally invasive hysterectomies with reduced recovery times",
        "specialized in reproductive endocrinology achieving 40% IVF success rates",
        "completed 200+ complex gynecologic oncology surgeries including radical hysterectomies",
        "performed 400+ urogynecologic procedures for pelvic floor disorders",
        "led maternal-fetal medicine unit managing 300+ cases of pregnancy complications"
    ]
}

# Special interests and expertise by specialty
EXPERTISE_STATEMENTS = {
    "Cardiology": [
        "Research focus on novel biomarkers for early detection of heart failure in diabetic patients. Published 15 peer-reviewed papers on cardiovascular risk stratification.",
        "Expertise in complex coronary interventions including chronic total occlusions. Proctor for new interventional cardiologists in advanced techniques.",
        "Special interest in preventive cardiology and lifestyle medicine. Developed comprehensive cardiac rehabilitation programs improving patient outcomes by 35%.",
        "Leading researcher in cardiac imaging techniques including 3D echocardiography and cardiac MRI. Established advanced imaging protocols adopted nationally.",
        "Focused on women's cardiovascular health and gender-specific risk factors. Founded specialized women's heart health clinic serving 500+ patients annually.",
        "Pioneer in telemedicine for cardiac monitoring. Implemented remote patient monitoring reducing readmissions by 40% in heart failure patients."
    ],
    "Neurosurgery": [
        "Research interest in brain-computer interfaces for paralyzed patients. Leading clinical trials for implantable neural devices with promising results.",
        "Expertise in minimally invasive spine surgery techniques. Developed novel approaches reducing surgical time by 30% and improving patient recovery.",
        "Special focus on pediatric brain tumors and epilepsy surgery. Established comprehensive pediatric neurosurgery program with multidisciplinary approach.",
        "Leading researcher in neurovascular surgery and cerebral bypass techniques. Published definitive textbook on microsurgical anatomy.",
        "Pioneer in awake craniotomy for eloquent area tumors. Achieved gross total resection in 85% of cases while preserving neurological function.",
        "Focused on traumatic brain injury outcomes. Developed protocols improving severe TBI survival rates by 25% through aggressive management."
    ],
    "Oncology": [
        "Research focus on precision medicine and targeted therapy selection. Leading investigator in multiple phase II and III clinical trials.",
        "Expertise in CAR-T cell therapy for hematologic malignancies. Achieved complete remission in 60% of refractory lymphoma cases.",
        "Special interest in cancer survivorship and quality of life. Established comprehensive survivorship clinic addressing long-term treatment effects.",
        "Pioneer in combination immunotherapy approaches. Published groundbreaking research on checkpoint inhibitor combinations improving response rates.",
        "Focused on geriatric oncology and treatment optimization for elderly patients. Developed frailty assessment tools adopted internationally.",
        "Leading researcher in liquid biopsies for early cancer detection. Principal investigator for multi-center screening trials."
    ],
    "Orthopedic Surgery": [
        "Research interest in biological approaches to cartilage regeneration. Leading clinical trials for stem cell therapies in osteoarthritis.",
        "Expertise in computer-assisted navigation for joint replacement. Achieved alignment within 2 degrees in 98% of knee replacements.",
        "Special focus on athlete care and return to sport protocols. Team physician for professional sports teams with excellent return-to-play outcomes.",
        "Pioneer in outpatient joint replacement surgery. Developed rapid recovery protocols allowing 90% same-day discharge for hip replacements.",
        "Focused on pediatric deformity correction including limb lengthening. Achieved excellent outcomes in 95% of complex reconstructions.",
        "Leading researcher in orthopedic biomechanics and implant design. Holds 5 patents for innovative surgical devices."
    ],
    "Pediatrics": [
        "Research focus on early intervention for autism spectrum disorders. Developed screening protocols identifying ASD 6 months earlier than standard.",
        "Expertise in pediatric obesity prevention and management. Led community programs reducing childhood obesity rates by 20% in target populations.",
        "Special interest in rare genetic disorders and metabolic diseases. Established specialized clinic diagnosing 50+ rare conditions annually.",
        "Pioneer in pediatric palliative care integration. Developed protocols improving quality of life for children with life-limiting conditions.",
        "Focused on adolescent mental health and suicide prevention. Implemented screening programs identifying at-risk youth with 85% accuracy.",
        "Leading researcher in pediatric infectious diseases and vaccine development. Principal investigator for novel vaccine trials."
    ],
    "Gastroenterology": [
        "Research interest in gut microbiome and its role in inflammatory bowel disease. Published seminal papers on microbiome-based therapies.",
        "Expertise in advanced endoscopic techniques including peroral endoscopic myotomy. Performed procedures avoiding surgery in 95% of achalasia cases.",
        "Special focus on fatty liver disease and metabolic syndrome. Developed integrated care model reducing disease progression by 40%.",
        "Pioneer in artificial intelligence for polyp detection. Implemented AI-assisted colonoscopy improving adenoma detection rates by 25%.",
        "Focused on celiac disease and gluten-related disorders. Established comprehensive center diagnosing 200+ cases annually.",
        "Leading researcher in pancreatic cancer early detection. Developing novel biomarker panels with 90% sensitivity for early-stage disease."
    ],
    "Urology": [
        "Research focus on immunotherapy for bladder cancer. Leading investigator for novel checkpoint inhibitor combinations showing promising results.",
        "Expertise in nerve-sparing techniques for prostate surgery. Achieved potency preservation in 85% of bilateral nerve-sparing procedures.",
        "Special interest in female pelvic medicine and reconstruction. Developed minimally invasive techniques for complex pelvic organ prolapse.",
        "Pioneer in focal therapy for prostate cancer. Implemented MRI-guided targeted treatments preserving quality of life in selected patients.",
        "Focused on pediatric urology and hypospadias outcomes. Achieved single-stage repair success in 95% of cases.",
        "Leading researcher in kidney stone prevention. Developed metabolic evaluation protocols reducing stone recurrence by 50%."
    ],
    "Dermatology": [
        "Research interest in melanoma immunotherapy resistance mechanisms. Leading clinical trials for combination treatments overcoming resistance.",
        "Expertise in complex wound healing and reconstruction. Developed protocols improving healing rates by 40% in chronic wounds.",
        "Special focus on pediatric vascular anomalies. Established multidisciplinary clinic treating 300+ complex cases annually.",
        "Pioneer in teledermatology and AI-assisted diagnosis. Implemented systems achieving 95% diagnostic accuracy for common conditions.",
        "Focused on ethnic skin and culturally sensitive dermatology. Published definitive guide on skin conditions in diverse populations.",
        "Leading researcher in psoriasis pathogenesis and treatment. Principal investigator for novel biologic therapies achieving PASI 90 in 70% of patients."
    ],
    "Neurology": [
        "Research focus on Alzheimer's disease biomarkers and early intervention. Leading investigator for disease-modifying therapy trials.",
        "Expertise in refractory epilepsy and surgical evaluation. Achieved seizure freedom in 70% of carefully selected surgical candidates.",
        "Special interest in autoimmune neurological disorders. Developed rapid diagnosis protocols reducing treatment delays by 50%.",
        "Pioneer in teleneurology for stroke care. Implemented hub-and-spoke model improving rural stroke outcomes significantly.",
        "Focused on neuromuscular disease genetic testing and counseling. Diagnosed 100+ rare genetic conditions using advanced sequencing.",
        "Leading researcher in migraine pathophysiology. Developed novel preventive strategies reducing migraine days by 60% in chronic sufferers."
    ],
    "Obstetrics and Gynecology": [
        "Research interest in preeclampsia prediction and prevention. Developed risk stratification model identifying 85% of cases before clinical onset.",
        "Expertise in fertility preservation for cancer patients. Achieved 45% pregnancy rates following oncofertility treatments.",
        "Special focus on minimally invasive surgery for endometriosis. Performed excisions achieving 80% pain reduction at 2-year follow-up.",
        "Pioneer in non-invasive prenatal testing implementation. Led adoption achieving 99% accuracy for common chromosomal abnormalities.",
        "Focused on global maternal health and reducing mortality. Implemented protocols in resource-limited settings saving 200+ lives annually.",
        "Leading researcher in uterine transplantation. Part of team achieving first successful pregnancies following transplant procedures."
    ]
}

def generate_doctor(index):
    """Generate a single doctor profile with realistic data"""
    
    # Generate basic information
    name = fake.name()
    doctor_name = f"Dr. {name}"
    
    # Select specialty and sub-specialty
    primary_specialty = random.choice(list(SPECIALTY_SUBSPECIALTY_MAP.keys()))
    sub_specialty = random.choice(SPECIALTY_SUBSPECIALTY_MAP[primary_specialty])
    
    # Select location and hospital
    location = random.choice(list(HOSPITAL_BY_LOCATION.keys()))
    hospital = random.choice(HOSPITAL_BY_LOCATION[location])
    
    # Generate years of experience (weighted towards mid-career)
    # Create a bell curve distribution for years of experience
    years_choices = list(range(5, 36))  # 5 to 35 years
    # Generate weights that peak around 15-20 years of experience
    years_weights = []
    for year in years_choices:
        if year < 10:
            weight = year - 4  # Gradually increase from 1 to 5
        elif year <= 20:
            weight = 6  # Peak weight for mid-career
        elif year <= 30:
            weight = 36 - year  # Gradually decrease from 5 to 1
        else:
            weight = 1  # Minimum weight for very senior
        years_weights.append(weight)
    
    years_of_experience = random.choices(years_choices, weights=years_weights)[0]
    
    # Select languages
    language_fluency = random.choice(LANGUAGES)
    
    # Generate critical surgeries summary
    base_summary = random.choice(SURGERY_SUMMARIES[primary_specialty])
    surgeries_summary = f"Dr. {name.split()[-1]} has {base_summary}. Maintains active involvement in clinical research and medical education, mentoring residents and fellows in advanced {sub_specialty.lower()} techniques."
    
    # Generate expertise statement
    expertise = random.choice(EXPERTISE_STATEMENTS[primary_specialty])
    
    return {
        "doctor_id": f"DOC-{index:05d}",
        "name": doctor_name,
        "primary_specialty": primary_specialty,
        "sub_specialty": sub_specialty,
        "location": location,
        "hospital_affiliation": hospital,
        "years_of_experience": years_of_experience,
        "language_fluency": language_fluency,
        "critical_surgeries_summary": surgeries_summary,
        "special_interests_and_expertise": expertise
    }

def generate_dataset(num_doctors=5000):
    """Generate the complete dataset of doctors"""
    
    print(f"Generating {num_doctors} doctor profiles...")
    doctors = []
    
    for i in range(1, num_doctors + 1):
        doctor = generate_doctor(i)
        doctors.append(doctor)
        
        # Progress indicator
        if i % 100 == 0:
            print(f"Generated {i}/{num_doctors} profiles...")
    
    return doctors

def save_to_json(doctors, filename="doctors_data.json"):
    """Save the doctor data to a JSON file"""
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(doctors, f, indent=2, ensure_ascii=False)
    
    print(f"\nSuccessfully saved {len(doctors)} doctor profiles to {filename}")
    
    # Calculate and display statistics
    specialties = {}
    locations = {}
    
    for doctor in doctors:
        spec = doctor["primary_specialty"]
        loc = doctor["location"]
        
        specialties[spec] = specialties.get(spec, 0) + 1
        locations[loc] = locations.get(loc, 0) + 1
    
    print("\nDataset Statistics:")
    print("-" * 40)
    print("Specialties Distribution:")
    for spec, count in sorted(specialties.items()):
        print(f"  {spec}: {count} doctors")
    
    print("\nLocation Distribution:")
    for loc, count in sorted(locations.items()):
        print(f"  {loc}: {count} doctors")

def main():
    """Main function to generate the dataset"""
    
    # Configuration
    NUM_DOCTORS = 5000  # Change this to generate more or fewer doctors
    OUTPUT_FILE = "doctors_data.json"
    
    # Generate the dataset
    doctors = generate_dataset(NUM_DOCTORS)
    
    # Save to JSON
    save_to_json(doctors, OUTPUT_FILE)
    
    # Generate a sample file with just 10 doctors for testing
    sample_doctors = doctors[:10]
    save_to_json(sample_doctors, "doctors_sample.json")
    print(f"\nAlso saved a sample of 10 doctors to doctors_sample.json for testing")

if __name__ == "__main__":
    main()