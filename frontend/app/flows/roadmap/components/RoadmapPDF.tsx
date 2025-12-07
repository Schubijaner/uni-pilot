import React from 'react';
import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
} from '@react-pdf/renderer';
import type { CareerPath, SemesterPlan, RoadmapTodo, Skill } from '~/types';

// Define styles
const styles = StyleSheet.create({
  page: {
    padding: 40,
    backgroundColor: '#FAFAFA',
    fontFamily: 'Helvetica',
  },
  header: {
    marginBottom: 30,
    textAlign: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  jobTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4F46E5',
    marginBottom: 16,
  },
  progressSection: {
    marginBottom: 30,
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    border: '1 solid #E5E7EB',
  },
  progressHeader: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 12,
  },
  progressBarContainer: {
    height: 20,
    backgroundColor: '#E5E7EB',
    borderRadius: 10,
    marginBottom: 8,
  },
  progressBar: {
    height: 20,
    backgroundColor: '#4F46E5',
    borderRadius: 10,
  },
  progressStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  progressStat: {
    fontSize: 12,
    color: '#6B7280',
  },
  semesterGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  semesterCard: {
    width: '48%',
    marginBottom: 20,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    border: '1 solid #E5E7EB',
  },
  semesterHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingBottom: 8,
    borderBottom: '1 solid #E5E7EB',
  },
  semesterTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  semesterProgress: {
    fontSize: 10,
    color: '#6B7280',
    backgroundColor: '#F3F4F6',
    padding: '4 8',
    borderRadius: 4,
  },
  todoItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
    paddingLeft: 4,
  },
  checkbox: {
    width: 14,
    height: 14,
    border: '2 solid #9CA3AF',
    borderRadius: 3,
    marginRight: 10,
    marginTop: 2,
  },
  checkboxChecked: {
    width: 14,
    height: 14,
    border: '2 solid #4F46E5',
    backgroundColor: '#4F46E5',
    borderRadius: 3,
    marginRight: 10,
    marginTop: 2,
  },
  todoText: {
    fontSize: 10,
    color: '#374151',
    flex: 1,
    lineHeight: 1.4,
  },
  todoTextCompleted: {
    fontSize: 10,
    color: '#9CA3AF',
    flex: 1,
    lineHeight: 1.4,
    textDecoration: 'line-through',
  },
  footer: {
    position: 'absolute',
    bottom: 30,
    left: 40,
    right: 40,
    textAlign: 'center',
    paddingTop: 16,
    borderTop: '1 solid #E5E7EB',
  },
  footerText: {
    fontSize: 10,
    color: '#9CA3AF',
  },
  notesSection: {
    marginTop: 20,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    border: '1 solid #E5E7EB',
    minHeight: 100,
  },
  notesTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 8,
  },
  notesLine: {
    borderBottom: '1 dashed #D1D5DB',
    marginBottom: 16,
    height: 20,
  },
  skillsSection: {
    marginBottom: 20,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    border: '1 solid #E5E7EB',
  },
  skillsTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 12,
  },
  skillsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  skillItem: {
    width: '50%',
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  skillName: {
    fontSize: 10,
    color: '#374151',
    flex: 1,
  },
  skillBarContainer: {
    width: 60,
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    marginRight: 8,
  },
  skillBar: {
    height: 8,
    backgroundColor: '#4F46E5',
    borderRadius: 4,
  },
});

interface RoadmapPDFProps {
  careerPath: CareerPath;
  userSkills: Skill[];
}

const TodoItemComponent: React.FC<{ todo: RoadmapTodo }> = ({ todo }) => (
  <View style={styles.todoItem}>
    <View style={todo.completed ? styles.checkboxChecked : styles.checkbox} />
    <Text style={todo.completed ? styles.todoTextCompleted : styles.todoText}>
      {todo.title}
    </Text>
  </View>
);

const SemesterCardComponent: React.FC<{ semester: SemesterPlan }> = ({ semester }) => {
  const completedCount = semester.todos.filter((t) => t.completed).length;
  const totalCount = semester.todos.length;

  return (
    <View style={styles.semesterCard}>
      <View style={styles.semesterHeader}>
        <Text style={styles.semesterTitle}>Semester {semester.semester}</Text>
        <Text style={styles.semesterProgress}>
          {completedCount}/{totalCount}
        </Text>
      </View>
      {semester.todos.map((todo) => (
        <TodoItemComponent key={todo.id} todo={todo} />
      ))}
    </View>
  );
};

export const RoadmapPDF: React.FC<RoadmapPDFProps> = ({ careerPath, userSkills }) => {
  const allTodos = careerPath.roadmap.flatMap((s) => s.todos);
  const completedTodos = allTodos.filter((t) => t.completed);
  const progress = allTodos.length > 0 ? Math.round((completedTodos.length / allTodos.length) * 100) : 0;

  const currentDate = new Date().toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <Document
      title={`Karriere-Roadmap: ${careerPath.jobName}`}
      author="UniPilot"
      subject="Personalisierte Karriere-Roadmap"
      creator="UniPilot"
    >
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.subtitle}>Deine personalisierte Karriere-Roadmap</Text>
          <Text style={styles.title}>Dein Weg zum</Text>
          <Text style={styles.jobTitle}>{careerPath.jobName}</Text>
          <Text style={styles.subtitle}>Erstellt am {currentDate}</Text>
        </View>

        {/* Overall Progress */}
        <View style={styles.progressSection}>
          <Text style={styles.progressHeader}>Gesamtfortschritt</Text>
          <View style={styles.progressBarContainer}>
            <View style={[styles.progressBar, { width: `${progress}%` }]} />
          </View>
          <View style={styles.progressStats}>
            <Text style={styles.progressStat}>{progress}% abgeschlossen</Text>
            <Text style={styles.progressStat}>
              {completedTodos.length} von {allTodos.length} Aufgaben erledigt
            </Text>
          </View>
        </View>

        {/* Required Skills Overview */}
        <View style={styles.skillsSection}>
          <Text style={styles.skillsTitle}>Benötigte Skills für {careerPath.jobName}</Text>
          <View style={styles.skillsGrid}>
            {careerPath.requiredSkills.slice(0, 6).map((skill) => {
              const userSkill = userSkills.find(
                (s) => s.name.toLowerCase() === skill.name.toLowerCase()
              );
              const userLevel = userSkill?.value || 0;
              const requiredLevel = skill.value || 100;
              const percentage = Math.min(100, (userLevel / requiredLevel) * 100);

              return (
                <View key={skill.name} style={styles.skillItem}>
                  <Text style={styles.skillName}>{skill.name}</Text>
                  <View style={styles.skillBarContainer}>
                    <View style={[styles.skillBar, { width: `${percentage}%` }]} />
                  </View>
                </View>
              );
            })}
          </View>
        </View>

        {/* Semester Plans */}
        <View style={styles.semesterGrid}>
          {careerPath.roadmap.slice(0, 4).map((semester) => (
            <SemesterCardComponent key={semester.semester} semester={semester} />
          ))}
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            UniPilot - Dein Karriere-Kompass für das Studium
          </Text>
        </View>
      </Page>

      {/* Second page if more than 4 semesters */}
      {careerPath.roadmap.length > 4 && (
        <Page size="A4" style={styles.page}>
          <View style={styles.header}>
            <Text style={styles.semesterTitle}>Semester-Aufgaben (Fortsetzung)</Text>
          </View>

          <View style={styles.semesterGrid}>
            {careerPath.roadmap.slice(4).map((semester) => (
              <SemesterCardComponent key={semester.semester} semester={semester} />
            ))}
          </View>

          {/* Notes Section */}
          <View style={styles.notesSection}>
            <Text style={styles.notesTitle}>Notizen</Text>
            <View style={styles.notesLine} />
            <View style={styles.notesLine} />
            <View style={styles.notesLine} />
            <View style={styles.notesLine} />
          </View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              UniPilot - Dein Karriere-Kompass für das Studium
            </Text>
          </View>
        </Page>
      )}

      {/* Notes and Tracking page */}
      <Page size="A4" style={styles.page}>
        <View style={styles.header}>
          <Text style={styles.semesterTitle}>Notizen & Tracking</Text>
        </View>

        {/* Manual Progress Tracking */}
        <View style={styles.progressSection}>
          <Text style={styles.progressHeader}>Fortschritt manuell tracken</Text>
          <Text style={[styles.progressStat, { marginBottom: 12 }]}>
            Male die Felder aus, wenn du Aufgaben abgeschlossen hast:
          </Text>
          <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
            {Array.from({ length: 20 }).map((_, i) => (
              <View
                key={i}
                style={{
                  width: 24,
                  height: 24,
                  border: '2 solid #D1D5DB',
                  borderRadius: 4,
                  margin: 4,
                }}
              />
            ))}
          </View>
        </View>

        {/* Weekly Goals */}
        <View style={styles.notesSection}>
          <Text style={styles.notesTitle}>Wochenziele</Text>
          {Array.from({ length: 5 }).map((_, i) => (
            <View key={i} style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
              <View style={styles.checkbox} />
              <View style={[styles.notesLine, { flex: 1, marginBottom: 0, marginLeft: 8 }]} />
            </View>
          ))}
        </View>

        {/* Free Notes */}
        <View style={[styles.notesSection, { flex: 1 }]}>
          <Text style={styles.notesTitle}>Freie Notizen</Text>
          {Array.from({ length: 10 }).map((_, i) => (
            <View key={i} style={styles.notesLine} />
          ))}
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            UniPilot - Dein Karriere-Kompass für das Studium
          </Text>
        </View>
      </Page>
    </Document>
  );
};

export default RoadmapPDF;
