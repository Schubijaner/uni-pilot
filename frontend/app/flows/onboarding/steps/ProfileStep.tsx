/**
 * ProfileStep - Profil-Eingabe im Onboarding
 * Formular für firstName, lastName, university, major mit Validierung
 */

import React, { useEffect, useState } from 'react';
import { getAllUniversities } from '../../../api/getAllUniversities';
import { Input, Card, CardHeader, CardTitle, CardDescription } from '~/components/ui';
import Select from '~/components/ui/Select';
import { useOnboarding } from '~/contexts';
import type { StudyProgram, University } from '~/types';
import { getStudyProgramsByUniversity } from '~/api/getStudyProgramsByUniversity';

export const ProfileStep: React.FC = () => {
  const { state, updateProfile, isProfileValid } = useOnboarding();
  const { profile } = state.userData;

  const [universities, setUniversities] = useState<University[]>([]);
  const [isLoadingUniversities, setIsLoadingUniversities] = useState(true);
  const [universityError, setUniversityError] = useState<string | null>(null);

  const [studyPrograms, setStudyPrograms] = useState<StudyProgram[]>([]);
  const [isLoadingStudyPrograms, setIsLoadingStudyPrograms] = useState(false);
  const [studyProgramError, setStudyProgramError] = useState<string | null>(null);


  useEffect(() => {
    const fetchUniversities = async () => {
      try {
        setIsLoadingUniversities(true);
        setUniversityError(null);
        const data = await getAllUniversities();
        setUniversities(data.items);
      } catch (error) {
        console.error('Failed to fetch universities:', error);
        setUniversityError('Universitäten konnten nicht geladen werden');
      } finally {
        setIsLoadingUniversities(false);
      }
    };

    fetchUniversities();
  }, []);

  useEffect(() => {
    const fetchStudyPrograms = async () => {
      if (!profile.university) {
        setStudyPrograms([]);
        return;
      }

      try {
        setIsLoadingStudyPrograms(true);
        setStudyProgramError(null);
        const data = await getStudyProgramsByUniversity(parseInt(profile.university, 10));
        setStudyPrograms(data.items);
      } catch (error) {
        console.error('Failed to fetch study programs:', error);
        setStudyProgramError('Studiengänge konnten nicht geladen werden');
      } finally {
        setIsLoadingStudyPrograms(false);
      }
    };

    fetchStudyPrograms();
  }, [profile.university]);

  const handleChange = (field: keyof typeof profile) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    updateProfile({ [field]: e.target.value });
  };

  const handleUniversityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    updateProfile({ university: e.target.value, major: '' }); // Reset major when university changes
  };

  const getError = (field: keyof typeof profile): string | undefined => {
    const value = profile[field];
    if (value !== undefined && value.length === 0) {
      return undefined; // Noch nicht angefasst
    }
    if (value?.trim() === '' && value.length > 0) {
      return 'Dieses Feld darf nicht leer sein';
    }
    return undefined;
  };

  const universityOptions = universities.map((uni) => ({
    value: uni.id.toString(),
    label: uni.name + (uni.abbreviation ? ` (${uni.abbreviation})` : ''),
  }));

  const studyProgramOptions = studyPrograms.map((program) => ({
    value: program.id.toString(),
    label: `${program.name} (${program.degree_type})`,
  }));

  return (
    <div className="max-w-xl mx-auto">
      <Card variant="glass">
        <CardHeader>
          <CardTitle>
            <span className="flex items-center gap-3">
              <span className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </span>
              Erzähl uns von dir
            </span>
          </CardTitle>
          <CardDescription>
            Diese Informationen helfen uns, personalisierte Empfehlungen zu erstellen.
          </CardDescription>
        </CardHeader>

        <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Vorname"
              placeholder="Max"
              value={profile.firstName}
              onChange={handleChange('firstName')}
              error={getError('firstName')}
              required
            />
            <Input
              label="Nachname"
              placeholder="Mustermann"
              value={profile.lastName}
              onChange={handleChange('lastName')}
              error={getError('lastName')}
              required
            />
          </div>

          <Select
            label="Universität"
            placeholder={isLoadingUniversities ? 'Lade Universitäten...' : 'Wähle deine Universität'}
            options={universityOptions}
            helperText={universityError || undefined}
            value={profile.university}
            onChange={(e) => updateProfile({ university: e.target.value })}
            disabled={isLoadingUniversities}
          />

          <Select
            label="Studiengang"
            placeholder={
              !profile.university
                ? 'Wähle zuerst deine Universität'
                : isLoadingStudyPrograms
                ? 'Lade Studiengänge...'
                : 'Wähle deinen Studiengang'
            }
            options={studyProgramOptions}
            helperText={studyProgramError || undefined}
            value={profile.major}
            onChange={(e) => updateProfile({ major: e.target.value })}
            disabled={!profile.university || isLoadingStudyPrograms}
          />
        </form>

        {/* Validation Status */}
        <div className="mt-6 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-2 text-sm">
            {isProfileValid ? (
              <>
                <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-green-600 dark:text-green-400">
                  Alle Felder ausgefüllt – Du kannst fortfahren
                </span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span className="text-amber-600 dark:text-amber-400">
                  Bitte fülle alle Felder aus
                </span>
              </>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ProfileStep;
