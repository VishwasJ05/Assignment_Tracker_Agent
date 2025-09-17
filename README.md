# Assignment Tracker AI Agent
### An Intelligent Web-Based System for Automated LMS Deadline Monitoring
**Technical Report**

**Vishwas Jasuja (B23303)**
b23303@students.iitmandi.ac.in

*September 17, 2025*

---

## Contents
1.  [Executive Summary](#1-executive-summary)
    - [1.1 Key Achievements](#11-key-achievements)
    - [1.2 Technology Stack](#12-technology-stack)
2.  [System Architecture and Design](#2-system-architecture-and-design)
    - [2.1 System Interaction Flow](#21-system-interaction-flow)
    - [2.2 Core Components and Rationale](#22-core-components-and-rationale)
3.  [Data Science and Performance](#3-data-science-and-performance)
    - [3.1 Classification Model Evaluation](#31-classification-model-evaluation)
    - [3.2 System Performance Benchmarks](#32-system-performance-benchmarks)
    - [3.3 Error Analysis](#33-error-analysis)
4.  [System Demonstration](#4-system-demonstration)
    - [4.1 Test Case: IIT Mandi Moodle LMS](#41-test-case-iit-mandi-moodle-lms)
    - [4.2 Demonstration Results](#42-demonstration-results)
5.  [Conclusion and Future Work](#5-conclusion-and-future-work)
    - [5.1 Future Enhancements](#51-future-enhancements)
- [Appendix: LLM Interaction Logs](#appendix-llm-interaction-logs)

---

## 1. Executive Summary

[cite_start]This report details the design, implementation, and performance of the Assignment Tracker AI Agent, an intelligent web application engineered to automate the monitoring of assignment deadlines from Learning Management Systems (LMS)[cite: 15]. [cite_start]The system integrates a robust web automation backend with a heuristic-based AI classifier, delivering a streamlined and user-friendly experience through an interactive web dashboard[cite: 16]. [cite_start]The primary objective of this project is to eliminate the manual effort required to track academic deadlines, thereby reducing the risk of missed submissions and improving students' organizational efficiency[cite: 17]. [cite_start]The agent authenticates into a given LMS, intelligently scrapes assignment data, classifies it with high accuracy, and presents a consolidated view of upcoming deadlines on a clean, accessible web interface[cite: 18].

### 1.1 Key Achievements
* [cite_start]**Interactive Web Dashboard**: A responsive user interface for seamless submission of credentials and clear visualization of results[cite: 20].
* [cite_start]**High-Accuracy AI Classification**: Achieved a 92% accuracy rate in distinguishing valid assignments from other course materials using a lightweight heuristic model[cite: 21].
* [cite_start]**Robust Automation Engine**: Attained 96.5% system reliability in data extraction through a multi-tiered Selenium-based scraping strategy[cite: 22].
* [cite_start]**Real-Time Processing**: Optimized to deliver results with an average end-to-end processing time of under 45 seconds per course page[cite: 23].

### 1.2 Technology Stack
[cite_start]Python 3.8+, Selenium WebDriver, SQLite, Heuristic AI Classification, and a Web Application Framework[cite: 25].

---

## 2. System Architecture and Design

[cite_start]The agent is architected as a client-server application, decoupling the user interface from the backend processing logic[cite: 27]. [cite_start]This modular design enhances scalability, security, and maintainability[cite: 28].

### 2.1 System Interaction Flow
[cite_start]The operational workflow is initiated by the user and executed by the backend in a sequential, automated process[cite: 30]:
1.  [cite_start]**User Input**: The user navigates to the Web Frontend, enters their LMS credentials and the target course URL, and submits the request[cite: 31].
2.  [cite_start]**Backend Request**: The frontend sends a secure request to the Backend Server, triggering the automation workflow[cite: 32].
3.  [cite_start]**Web Automation**: The Selenium Scraper module launches a headless browser instance, authenticates into the LMS, and navigates to the specified URL[cite: 33]. [cite_start]It then extracts the raw page content[cite: 34].
4.  [cite_start]**AI-Powered Filtering**: The extracted content is passed to the AI Classifier, which analyzes the text to identify and filter valid assignment entries[cite: 35].
5.  [cite_start]**Data Persistence**: Verified assignments and their metadata (name, due date) are parsed and stored in a centralized SQLite Database[cite: 39].
6.  [cite_start]**Results Display**: The backend API queries the database for the results of the recent scan and sends the formatted data back to the web frontend, which dynamically renders it on the user's dashboard[cite: 40].

![System Architecture Diagram](https://i.imgur.com/Qh0G3iM.png)
[cite_start]*Figure 1: System architecture and data flow of the Assignment Tracker AI Agent, showing the interaction between the web frontend, backend server, and the Selenium automation engine[cite: 53].*

### 2.2 Core Components and Rationale

* [cite_start]**Web Frontend**: A responsive web interface serves as the primary entry point for the user[cite: 55]. [cite_start]Its design prioritizes simplicity and ease of use, allowing users to quickly initiate the scraping process[cite: 56].
* **Backend Server**: The central logic hub of the application. [cite_start]It manages user requests, orchestrates the different modules, and handles data transmission[cite: 57]. [cite_start]A server-based model was chosen to centralize the complex automation logic and keep the client interface lightweight[cite: 58].
* [cite_start]**Selenium Web Scraper**: Selenium WebDriver was selected for its unparalleled ability to interact with dynamic, JavaScript-heavy web pages typical of modern LMS platforms[cite: 59]. [cite_start]It simulates real user actions, ensuring robust and reliable data extraction where static scrapers would fail[cite: 60].
* [cite_start]**AI Classifier**: A Weighted Heuristic Engine provides a lightweight yet powerful solution for classification[cite: 61]. [cite_start]This approach was chosen over more complex deep learning models because it offers high accuracy for this specific domain without incurring significant computational overhead, making the system fast and efficient[cite: 62].
* [cite_start]**SQLite Database**: A local SQLite database provides a simple, serverless, and file-based persistence layer[cite: 63]. [cite_start]It is ideal for this application's scale, offering fast query performance and zero-configuration setup, simplifying deployment and maintenance[cite: 64].

---

## 3. Data Science and Performance
[cite_start]The effectiveness of the agent hinges on the accuracy of its AI classifier and the efficiency of its data processing pipeline[cite: 66].

### 3.1 Classification Model Evaluation
[cite_start]The heuristic model was evaluated against a manually labeled dataset of 50 distinct LMS pages using 5-fold cross-validation[cite: 71]. [cite_start]The baseline represents a simple keyword-matching approach[cite: 72].

**Table 1: AI Classification Performance Metrics**
| Metric    | Heuristic Model | Baseline | Improvement |
|-----------|-----------------|----------|-------------|
| Accuracy  | 92.0%           | 65.0%    | +41.5%      |
| Precision | 89.0%           | 60.0%    | +48.3%      |
| Recall    | 94.0%           | 70.0%    | +34.3%      |
| F1-Score  | 91.4%           | 64.6%    | +41.5%      |
[cite_start]*[cite: 74]*

### 3.2 System Performance Benchmarks
[cite_start]Performance was benchmarked across 100+ test runs on a standard development machine to measure real-world efficiency[cite: 76].

**Table 2: System Performance Benchmarks**
| Metric                | Value | Unit    | Justification                                      |
|-----------------------|-------|---------|----------------------------------------------------|
| Avg. End-to-End Time  | 45    | sec     | Measured from user submission to results display.  |
| Peak Memory Usage     | 85    | MB      | Primarily driven by the Chrome WebDriver instance. |
| Database Query Time   | 12    | ms      | Average time to retrieve results from SQLite.      |
| Classification Speed  | 0.8   | ms/item | Demonstrates high efficiency of the heuristic model.|
[cite_start]*[cite: 78]*

### 3.3 Error Analysis
[cite_start]An analysis of 1,000 operational runs identified the primary sources of error, with date parsing being the most common challenge due to inconsistent LMS formats[cite: 80].

![Error Distribution Chart](https://i.imgur.com/kF2A8xS.png)
[cite_start]*Figure 2: Error Distribution Analysis* [cite: 94]

---

## 4. System Demonstration

### 4.1 Test Case: IIT Mandi Moodle LMS
[cite_start]A live test was conducted using a course page from the IIT Mandi LMS to demonstrate the end-to-end functionality of the system[cite: 100].

* [cite_start]**Input URL**: `https://lms.iitmandi.ac.in/course/view.php?id=4547` [cite: 101]

[cite_start]The user enters their credentials and the URL into the web interface[cite: 102]. [cite_start]Upon submission, the backend processes the request and returns the extracted deadlines, which are then displayed on the "Upcoming Deadlines" dashboard[cite: 103].

![Application Dashboard](https://i.imgur.com/your-image-url.png)
[cite_start]*Figure 3: The web application's dashboard displaying the extracted deadlines from the IIT Mandi LMS[cite: 144].*

### 4.2 Demonstration Results
* [cite_start]**Extraction**: Successfully identified and extracted 4 upcoming assignments[cite: 106].
* [cite_start]**Classification**: All items were correctly classified with an average confidence score of 93.5%[cite: 107].
* [cite_start]**Performance**: The results were displayed to the user in 42 seconds[cite: 108].
* [cite_start]**Extracted Assignments**[cite: 109]:
    1.  [cite_start]Assignment 1 Due: Tuesday, 19 August 2025, 12:00 AM [cite: 110]
    2.  [cite_start]Assignment 2: Logic and Automated Reasoning Due: Saturday, 30 August 2025, 11:59 PM [cite: 111]
    3.  [cite_start]Assignment 3 - Due: Tuesday, 16 September 2025, 11:59 PM [cite: 112]
    4.  [cite_start]Assignment 4 Due: Thursday, 25 September 2025, 11:59 PM [cite: 113]

---

## 5. Conclusion and Future Work
[cite_start]The Assignment Tracker AI Agent successfully meets its objective of providing a reliable, automated solution for monitoring academic deadlines[cite: 115]. [cite_start]By leveraging a modern web architecture, robust automation tools, and efficient AI, it offers a valuable service that enhances student productivity and organization[cite: 116].

### 5.1 Future Enhancements
[cite_start]The modular architecture provides a strong foundation for future development[cite: 118]. [cite_start]The planned roadmap includes[cite: 118]:
1.  [cite_start]**User Accounts & Historical Tracking**: Implement a full user authentication system to save scraping history and track completed assignments[cite: 119].
2.  [cite_start]**Expanded LMS Support**: Develop dedicated parsing modules for other popular LMS platforms like Canvas and Blackboard[cite: 120].
3.  [cite_start]**Calendar Integration**: Add functionality to export deadlines to popular calendar services like Google Calendar and Outlook Calendar[cite: 121].
4.  [cite_start]**Advanced Notification System**: Re-introduce a notification system (e.g., email, push notifications) tied to user accounts for proactive deadline reminders[cite: 122].

---

## Appendix: LLM Interaction Logs
[cite_start]This appendix provides links to the development and debugging conversations with Large Language Models (LLMs) that were instrumental in this project's creation[cite: 146]. [cite_start]These logs offer insight into the iterative process of code generation, logic refinement, and problem-solving[cite: 147].

* [cite_start]**ChatGPT Conversation Log**: Details initial brainstorming, generation of the core Selenium scraper code, and refinement of the heuristic classification logic[cite: 152].
    * [cite_start]**Link**: [https://chatgpt.com/share/68c9cb89-2a34-8008-904d-5eb10a509d26](https://chatgpt.com/share/68c9cb89-2a34-8008-904d-5eb10a509d26) [cite: 153]
* [cite_start]**Claude Conversation Log**: Covers the architectural design, structuring the project into classes, implementing the SQLite database module, and developing the notification system logic[cite: 155].
    * [cite_start]**Link**: [https://claude.ai/public/artifacts/8cd23496-8b0d-4fe4-a395-00d71d50370d](https://claude.ai/public/artifacts/8cd23496-8b0d-4fe4-a395-00d71d50370d) [cite: 156]
