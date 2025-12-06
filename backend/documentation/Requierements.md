# Agent Prompt – Career Orientation App

## **Ziel**
Basierend auf den Informationen im `README.md` möchten wir eine App entwickeln, die Studierende bei ihrer Karriereplanung unterstützt und ihnen passende Karrierewege, Empfehlungen und Lernpfade (Roadmaps) aufzeigt.

## **Funktionen der App**

### **1. User Management**
- Registrierung und Login
- Speicherung persönlicher Daten und Fortschritt

---

### **2. Zwei Hauptkomponenten**

## **(A) Onboarding & Career-Tree**
Während des Onboardings gibt der/die Studierende Folgendes an:

- Universität  
- Studiengang  
- Semester  
- Abgeschlossene Module  

Auf Basis dieser Eingaben soll ein **Karrierebaum (Career Tree)** generiert werden:

- Die Endknoten repräsentieren verschiedene **Themenfelder** (z. B. *Full Stack Development*, *Backend Development*, *Frontend Development*, *Data Science*, *Machine Learning*).  
- Diese Themenfelder müssen auf dem jeweiligen Studiengang basieren (z. B. Informatik → technische Bereiche; Wirtschaftsinformatik → Data Analytics etc.).
- Der/die Studierende wählt anschließend **ein Themenfeld** aus.
- Danach wird automatisch eine **Roadmap** für dieses Themenfeld generiert.

---

## **(B) Roadmap-Generierung**
Die Roadmap soll:

- die Schritte zeigen, die notwendig sind, um das ausgewählte Karriereziel zu erreichen  
- relevante Kurse, Module, Fähigkeiten und Projekte empfehlen  
- Module aus dem Modulhandbuch einbeziehen und kennzeichnen, welche besonders hilfreich oder wichtig sind  
- **zeitlich strukturiert** sein  
  - nach Semestern  
  - nach Semesterferien (z. B. Praktika, Bootcamps, Zertifikate)

Der/die Studierende beantwortet anschließend gezielte Fragen.  
Die Antworten sollen:

- den Career-Tree dynamisch anpassen  
- ggf. zu einem neuen Themenfeld führen  
- die Roadmap automatisch aktualisieren  

---

## **(C) Chat für jedes Themenfeld**
- Für **jedes Themenfeld** im Career-Tree gibt es eine eigene Chatbox.  
- Der Chat verwendet ein vordefiniertes System-Prompt und liefert:
  - präzise und kurze Beschreibungen des jeweiligen Themenfeldes
  - Expertenantworten zu Fragen der Studierenden
  - Hinweise zu Skills, Tools, Einstiegsmöglichkeiten  

---

### **3. Bilder als Referenz**
Wir stellen zwei Bilder bereit:

1. Userflows der App  
2. Grobes Datenbank-Schema  

Diese dienen als Grundlage für das Datenmodell.

---

s### **4. Datenbank-Schema**
Die Datenbank soll folgende Entitäten abbilden:

- Nutzerprofile  
- Module (Pflicht + Wahlmodule)  
- Karrierebaum (Themenfelder, Knoten, Beziehungen)  
- Roadmaps  
- Empfehlungen (Kurse, Bücher, Projekte, Skills)  
- Fortschritt des/der Studierenden (z. B. erledigte Module, bearbeitete Roadmap-Einträge)

---

---
### **5. AI-Features, die die App unterstützen muss**

#### **1. LLM-gestützter Chat für jedes Themenfeld**
Für jedes Themenfeld soll ein eigener Chatbot zur Verfügung stehen.  
Der Chatbot nutzt eine LLM-Anbindung und kann:
s
- das jeweilige Themenfeld verständlich erklären  
- einen ersten Überblick zu Inhalten, Skills und typischen Aufgaben geben  
- Fragen der Studierenden präzise beantworten  

Ziel: Studierende sollen schnell nachvollziehen können, ob ein Themenfeld zu ihren Interessen passt.

---

#### **2. LLM-gestützte Generierung der Roadmap**
Die Roadmap wird automatisch durch ein LLM erzeugt.  
Der Prompt an das LLM umfasst Informationen wie:

- Studiengang  
- Skills  
- aktuelles Semester  
- mögliche Wahlpflichtfächer  
- gewähltes Themenfeld  

Auf dieser Basis soll das LLM eine Roadmap generieren, die sich am Datenschema orientiert und u. a. folgende Empfehlungen enthält:

- welche Wahlpflichtmodule sinnvoll sind  
- welche Bücher oder Ressourcen hilfreich sind  
- relevante Bootcamps oder Online-Kurse  
- Empfehlungen für Praktika oder Werkstudentenstellen  
- Skills, die aufgebaut werden sollten  
- Vorschläge für Projekte (Uni-, Privat- oder GitHub-Projekte)

Ziel: Der/die Studierende soll eine strukturierte, praxisnahe und realistische Orientierung erhalten, um optimal für das gewählte Themenfeld ausgebildet zu werden.