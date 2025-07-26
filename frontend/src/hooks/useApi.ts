// src/hooks/useApi.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as coursesAPI from '../api/courses';
import * as quizzesAPI from '../api/quizzes';
import * as usersAPI from '../api/users';
import * as notificationsAPI from '../api/notifications';
import * as authAPI from '../api/auth';
import * as profileAPI from '../api/profile';
import { User } from '../api/auth'; // Assuming User type is exported from auth API

// Course hooks
export function useCourses(params?: Parameters<typeof coursesAPI.getCourses>[0]) {
  return useQuery({
    queryKey: ['courses', params],
    queryFn: () => coursesAPI.getCourses(params),
  });
}

export function useCourse(id: string) {
  return useQuery({
    queryKey: ['course', id],
    queryFn: () => coursesAPI.getCourse(id),
    enabled: !!id,
  });
}

export function useCreateCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: coursesAPI.createCourse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
}

export function useUpdateCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<coursesAPI.Course> }) =>
      coursesAPI.updateCourse(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['course', id] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
}

export function useDeleteCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: coursesAPI.deleteCourse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
}

export function useEnrollInCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: coursesAPI.enrollInCourse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['enrollments'] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
}

export function useUserEnrollments() {
  return useQuery({
    queryKey: ['enrollments'],
    queryFn: coursesAPI.getUserEnrollments,
  });
}

// Quiz hooks
export function useQuizzes(params?: Parameters<typeof quizzesAPI.getQuizzes>[0]) {
  return useQuery({
    queryKey: ['quizzes', params],
    queryFn: () => quizzesAPI.getQuizzes(params),
  });
}

export function useQuiz(id: string) {
  return useQuery({
    queryKey: ['quiz', id],
    queryFn: () => quizzesAPI.getQuiz(id),
    enabled: !!id,
  });
}

export function useCreateQuiz() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: quizzesAPI.createQuiz,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quizzes'] });
    },
  });
}

export function useUpdateQuiz() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<quizzesAPI.Quiz> }) =>
            quizzesAPI.updateQuiz(id, data),
        onSuccess: (_, { id }) => {
            queryClient.invalidateQueries({ queryKey: ['quiz', id] });
            queryClient.invalidateQueries({ queryKey: ['quizzes'] });
        },
    });
}

export function useDeleteQuiz() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: quizzesAPI.deleteQuiz,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['quizzes'] });
        },
    });
}

export function usePublishQuiz() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: string) => quizzesAPI.publishQuiz(id),
        onSuccess: (_, id) => {
            queryClient.invalidateQueries({ queryKey: ['quiz', id] });
            queryClient.invalidateQueries({ queryKey: ['quizzes'] });
        },
    });
}

export function useSubmitQuiz() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ quizId, answers }: { quizId: string; answers: any[] }) =>
            quizzesAPI.submitQuiz(quizId, answers),
        onSuccess: (data, variables) => {
            queryClient.invalidateQueries({ queryKey: ['quiz', variables.quizId] });
            queryClient.invalidateQueries({ queryKey: ['userQuizAttempts'] });
        },
    });
}

export function useQuizAttempts(quizId: string) {
    return useQuery({
        queryKey: ['quizAttempts', quizId],
        queryFn: () => quizzesAPI.getQuizAttempts(quizId),
        enabled: !!quizId,
    });
}

export function useUserQuizAttempts(userId?: string, quizId?: string) {
    return useQuery({
        queryKey: ['userQuizAttempts', userId, quizId],
        queryFn: () => quizzesAPI.getUserQuizAttempts(userId, quizId),
        enabled: !!userId && !!quizId,
    });
}

export function useQuizStats(quizId: string) {
    return useQuery({
        queryKey: ['quizStats', quizId],
        queryFn: () => quizzesAPI.getQuizStats(quizId),
        enabled: !!quizId,
    });
}

export function useUserQuizStats(userId: string) {
    return useQuery({
        queryKey: ['userQuizStats', userId],
        queryFn: () => quizzesAPI.getUserQuizStats(userId),
        enabled: !!userId,
    });
}

export function useExportQuizResults() {
    return useMutation({
        mutationFn: (quizId: string) => quizzesAPI.exportQuizResults(quizId),
    });
}


export function useQuizSubmission(submissionId?: string) {
  return useQuery({
    queryKey: ['quizSubmission', submissionId],
    queryFn: () => quizzesAPI.getQuizSubmission(submissionId!),
    enabled: !!submissionId
  });
}


// User hooks
export function useUsers(params?: Parameters<typeof usersAPI.getUsers>[0]) {
  return useQuery({
    queryKey: ['users', params],
    queryFn: () => usersAPI.getUsers(params),
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: () => usersAPI.getUser(id),
    enabled: !!id,
  });
}

export function useCreateUser() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: usersAPI.createUser,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
        },
    });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<User> }) =>
      usersAPI.updateUser(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['user', id] });
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useDeleteUser() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: usersAPI.deleteUser,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
        },
    });
}


// Notification hooks
export function useNotifications(userId?: string) {
  return useQuery({
    queryKey: ['notifications', userId],
    queryFn: () => notificationsAPI.getNotifications(),
    enabled: !!userId,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useNotification(id: string) {
    return useQuery({
        queryKey: ['notification', id],
        queryFn: () => notificationsAPI.getNotification(id),
        enabled: !!id,
    });
}

export function useMarkNotificationAsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationsAPI.markNotificationAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

export function useDeleteNotification() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: string) => notificationsAPI.deleteNotification(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
        },
    });
}


export function useMarkAllNotificationsAsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => notificationsAPI.markAllNotificationsAsRead(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

export function useDeleteAllNotifications() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => notificationsAPI.deleteAllNotifications(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

export function useNotificationSettings(userId?: string) {
    return useQuery({
        queryKey: ['notificationSettings', userId],
        queryFn: () => userId ? notificationsAPI.getNotificationSettings(userId) : Promise.reject('No userId'),
        enabled: !!userId,
    });
}

export function useUpdateNotificationSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, settings }: { userId: string; settings: any }) =>
      notificationsAPI.updateNotificationSettings({ userId, settings }),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: ['notificationSettings', userId] });
    },
  });
}


// Profile hooks
export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) =>
      profileAPI.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] });
      queryClient.invalidateQueries({ queryKey: ['userStats'] });
    },
  });
}

export function useUploadAvatar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, file }: { userId: string; file: File }) =>
      profileAPI.uploadAvatar({ userId, file }),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: ['user', userId] });
    },
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: (data: any) => authAPI.changePassword(data),
  });
}

export function useDeleteAccount() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (userId: string) => authAPI.deleteAccount(userId),
        onSuccess: () => {
            queryClient.invalidateQueries(); // Invalidate all queries on account deletion
        },
    });
}

export function useUserStats(userId?: string) {
  return useQuery({
    queryKey: ['userStats', userId],
    queryFn: () => profileAPI.getUserStats(userId!),
    enabled: !!userId,
  });
}

export function useUserActivity(userId?: string) {
  return useQuery({
    queryKey: ['userActivity', userId],
    queryFn: () => profileAPI.getUserActivity(userId!),
    enabled: !!userId,
  });
}

export function useUserCourses(userId?: string) {
  return useQuery({
    queryKey: ['userCourses', userId],
    queryFn: () => profileAPI.getUserCourses(userId!),
    enabled: !!userId,
  });
}

export function useUserAchievements(userId?: string) {
  return useQuery({
    queryKey: ['userAchievements', userId],
    queryFn: () => profileAPI.getUserAchievements(userId!),
    enabled: !!userId,
  });
}


// Main API hook to be used in components
export const useApi = () => ({
  // Course hooks
  useCourses,
  useCourse,
  createCourse: useCreateCourse(),
  updateCourse: useUpdateCourse(),
  deleteCourse: useDeleteCourse(),
  enrollInCourse: useEnrollInCourse(),
  useUserEnrollments,

  // Quiz hooks
  useQuizzes,
  useQuiz,
  createQuiz: useCreateQuiz(),
  updateQuiz: useUpdateQuiz(),
  deleteQuiz: useDeleteQuiz(),
  publishQuiz: usePublishQuiz(),
  submitQuiz: useSubmitQuiz(),
  useQuizAttempts,
  useUserQuizAttempts,
  useQuizStats,
  useUserQuizStats,
  exportQuizResults: useExportQuizResults,
  useQuizSubmission,

  // User hooks
  useUsers,
  useUser,
  createUser: useCreateUser(),
  updateUser: useUpdateUser(),
  deleteUser: useDeleteUser(),

  // Notification hooks
  useNotifications,
  useNotification,
  markNotificationAsRead: useMarkNotificationAsRead(),
  deleteNotification: useDeleteNotification(),
  markAllNotificationsAsRead: useMarkAllNotificationsAsRead(),
  deleteAllNotifications: useDeleteAllNotifications(),
  useNotificationSettings,
  updateNotificationSettings: useUpdateNotificationSettings(),

  // Profile hooks
  updateProfile: useUpdateProfile(),
  uploadAvatar: useUploadAvatar(),
  changePassword: useChangePassword(),
  deleteAccount: useDeleteAccount(),
  useUserStats,
  useUserActivity,
  useUserCourses,
  useUserAchievements,
});
