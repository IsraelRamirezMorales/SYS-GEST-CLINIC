import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Search, Eye, EyeOff, Camera, CheckCircle2, AlertCircle, Info, Image, Trash2, X, User, Key } from 'lucide-react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://cl-nica-remes.onrender.com');

const getSessionDisplayText = (sesion_type, doctor_charge) => {
  const docId = parseInt(doctor_charge);
  if (sesion_type === 'Consulta') {
    if (docId === 5) return 'Consulta - Dra. Gabriela';
    if (docId === 8) return 'Consulta - Dra. Valeria';
    return 'Consulta';
  }
  if (sesion_type === 'Terapia') {
    if (docId === 5) return 'Terapia - Fis. Alejandro';
    if (docId === 8) return 'Terapia - Fis. Patricia';
    return 'Terapia';
  }
  if (sesion_type === 'Alberca') {
    return 'Alberca - Fis. Eduardo';
  }
  return sesion_type;
};

const formatSessionDate = (dateStr) => {
  if (!dateStr) return '';
  const cleanDateStr = typeof dateStr === 'string' ? dateStr.split('T')[0] : '';
  const parts = cleanDateStr.split('-');
  if (parts.length !== 3) return dateStr;
  
  const year = parseInt(parts[0], 10);
  const monthIdx = parseInt(parts[1], 10) - 1;
  const day = parseInt(parts[2], 10);
  
  const months = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
  ];
  
  return `${day} de ${months[monthIdx]} del ${year}`;
};

function App() {
  // Auth state
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState('');
  const [usernameInput, setUsernameInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [profilePictureUploading, setProfilePictureUploading] = useState(false);

  // Custom Alert Modal State
  const [modalAlert, setModalAlert] = useState({
    show: false,
    type: 'success', // 'success' | 'error' | 'info'
    title: '',
    message: '',
    onConfirm: null
  });

  const showAlert = (title, message, type = 'success', onConfirm = null) => {
    setModalAlert({
      show: true,
      type,
      title,
      message,
      onConfirm
    });
  };

  // Profile picture modal states
  const [showOptionsModal, setShowOptionsModal] = useState(false);
  const [showCameraModal, setShowCameraModal] = useState(false);
  const [cropImage, setCropImage] = useState(null); // Data URL of image to crop
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [imageDisplaySize, setImageDisplaySize] = useState({ width: 280, height: 280 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [stream, setStream] = useState(null);

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const imgRef = useRef(null);

  const handleSelectFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = () => {
      setCropImage(reader.result);
      setShowOptionsModal(false);
    };
    reader.readAsDataURL(file);
    e.target.value = "";
  };

  const handleCameraOption = () => {
    setShowOptionsModal(false);
    setShowCameraModal(true);
    startCamera();
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 640, height: 640 },
        audio: false
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      showAlert("Error de Cámara", "No se pudo acceder a la cámara. Asegúrate de otorgar los permisos necesarios.", "error");
      setShowCameraModal(false);
    }
  };

  const capturePhoto = () => {
    const video = videoRef.current;
    if (!video) return;
    
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 640;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg');
    
    stopCamera();
    setShowCameraModal(false);
    setCropImage(dataUrl);
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setOffset({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleTouchStart = (e) => {
    if (e.touches.length === 1) {
      setIsDragging(true);
      setDragStart({ 
        x: e.touches[0].clientX - offset.x, 
        y: e.touches[0].clientY - offset.y 
      });
    }
  };

  const handleTouchMove = (e) => {
    if (!isDragging || e.touches.length !== 1) return;
    setOffset({
      x: e.touches[0].clientX - dragStart.x,
      y: e.touches[0].clientY - dragStart.y
    });
  };

  const handleImageLoad = (e) => {
    const { naturalWidth, naturalHeight } = e.target;
    let displayWidth = 280;
    let displayHeight = 280;
    const aspectRatio = naturalWidth / naturalHeight;
    if (aspectRatio > 1) {
      displayHeight = 280;
      displayWidth = 280 * aspectRatio;
    } else {
      displayWidth = 280;
      displayHeight = 280 / aspectRatio;
    }
    setImageDisplaySize({ width: displayWidth, height: displayHeight });
    setOffset({ x: 0, y: 0 });
    setScale(1);
  };

  const handleSaveCrop = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 400;
    canvas.height = 400;
    const ctx = canvas.getContext('2d');
    
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, 400, 400);
    
    const img = imgRef.current;
    if (!img) return;
    
    const F = 400 / 280;
    const drawWidth = imageDisplaySize.width * scale * F;
    const drawHeight = imageDisplaySize.height * scale * F;
    const drawCenterX = 200 + offset.x * F;
    const drawCenterY = 200 + offset.y * F;
    
    ctx.drawImage(img, drawCenterX - drawWidth / 2, drawCenterY - drawHeight / 2, drawWidth, drawHeight);
    
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const croppedFile = new File([blob], "profile_picture.jpg", { type: "image/jpeg" });
      setCropImage(null);
      await uploadCroppedPicture(croppedFile);
    }, 'image/jpeg', 0.9);
  };

  const uploadCroppedPicture = async (file) => {
    setProfilePictureUploading(true);
    const formData = new FormData();
    formData.append("id_employees", user.id_employees);
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/profile/upload_picture/`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.ok) {
        const updatedUser = { ...user, profile_picture: data.url };
        setUser(updatedUser);
        localStorage.setItem("clinica_user", JSON.stringify(updatedUser));
        showAlert("¡Éxito!", "Foto de perfil actualizada correctamente.", "success");
      } else {
        showAlert("Error", "Error al subir la foto: " + (data.error || ""), "error");
      }
    } catch (err) {
      console.error(err);
      showAlert("Error de Conexión", "No se pudo establecer conexión con el servidor al subir la foto.", "error");
    } finally {
      setProfilePictureUploading(false);
    }
  };

  const handleDeleteProfilePicture = async () => {
    setProfilePictureUploading(true);
    try {
      const res = await fetch(`${API_URL}/profile/delete_picture/`, {
        method: "POST",
        body: new URLSearchParams({ id_employees: user.id_employees })
      });
      const data = await res.json();
      if (data.ok) {
        const updatedUser = { ...user, profile_picture: null };
        setUser(updatedUser);
        localStorage.setItem("clinica_user", JSON.stringify(updatedUser));
        showAlert("¡Éxito!", "Foto de perfil eliminada correctamente.", "success");
        setShowOptionsModal(false);
      } else {
        showAlert("Error", "Error al eliminar la foto: " + (data.error || ""), "error");
      }
    } catch (err) {
      console.error(err);
      showAlert("Error de Conexión", "No se pudo establecer conexión con el servidor.", "error");
    } finally {
      setProfilePictureUploading(false);
    }
  };

  // View navigation state: 'login', 'menu', 'calendar', 'appointments', 'add_patient', 'all_patients', 'add_session', 'edit_patient_info'
  const [currentView, setCurrentView] = useState('login');

  // Navigation History stack to allow easy back button tracking
  const [history, setHistory] = useState([]);

  // Caching states
  const [patients, setPatients] = useState([]);
  const [patientsLoading, setPatientsLoading] = useState(false);
  const [patientsFetched, setPatientsFetched] = useState(false);

  const [appointments, setAppointments] = useState([]);
  const [appointmentsLoading, setAppointmentsLoading] = useState(false);
  const [appointmentsFetched, setAppointmentsFetched] = useState(false);

  const [fisioType, setFisioType] = useState('');

  // Dialog / Modal state
  const [showAttendanceDialog, setShowAttendanceDialog] = useState(false);
  const [attendanceSessionId, setAttendanceSessionId] = useState(null);

  const [showNotesDialog, setShowNotesDialog] = useState(false);
  const [notesPatientId, setNotesPatientId] = useState(null);
  const [notesText, setNotesText] = useState('');

   const [showInstructionsModal, setShowInstructionsModal] = useState(false);
  const [instructionsText, setInstructionsText] = useState('');

  const [showConsultationModal, setShowConsultationModal] = useState(false);
  const [consultationPatient, setConsultationPatient] = useState(null);
  const [consultationText, setConsultationText] = useState('');
  const [exportingPdf, setExportingPdf] = useState(false);

  // New Patient Form state
  const [newPatient, setNewPatient] = useState({
    name: '',
    last_name: '',
    phone: '',
    doctor_sender: '',
    doctor_selected: '',
    instructions: '',
    aseguradora: ''
  });

  // Collision Dialog state
  const [showCollisionDialog, setShowCollisionDialog] = useState(false);
  const [collisionText, setCollisionText] = useState('');
  const [pendingSessionData, setPendingSessionData] = useState(null);

  // Duplicate Patient Validation state
  const [showDuplicateBlockDialog, setShowDuplicateBlockDialog] = useState(false);
  const [showDuplicateConfirmDialog, setShowDuplicateConfirmDialog] = useState(false);
  const [pendingPatientData, setPendingPatientData] = useState(null);

  // Change Session Date state
  const [showChangeDateDialog, setShowChangeDateDialog] = useState(false);
  const [changeDateSessionId, setChangeDateSessionId] = useState(null);
  const [changeDateValue, setChangeDateValue] = useState('');
  const [changeTimeValue, setChangeTimeValue] = useState('');

  // Password visibility state
  const [showPassword, setShowPassword] = useState(false);

  // Edit Patient Info Form state
  const [editPatientForm, setEditPatientForm] = useState({
    id_patient: '',
    name: '',
    last_name: '',
    phone: '',
    doctor_sender: '',
    amount_to_pay: 0
  });

  // New Session Form state
  const [newSession, setNewSession] = useState({
    id_patient: '',
    entry_date: new Date().toISOString().split('T')[0],
    entry_time: '09:00:00',
    sesion_type: 'Consulta'
  });

  // Search state
  const [patientSearch, setPatientSearch] = useState('');
  const [appointmentsSearch, setAppointmentsSearch] = useState('');
  const [apptFilter, setApptFilter] = useState('day');

  // Selected Date for calendar view (TableCalendar replica)
  const [calendarDate, setCalendarDate] = useState(new Date());

  const [reportsData, setReportsData] = useState(null);
  const [reportsLoading, setReportsLoading] = useState(false);
  const [reportFilter, setReportFilter] = useState('week');
  const [typeFilter, setTypeFilter] = useState('Consulta');

  const fetchReports = async () => {
    if (!user) return;
    setReportsLoading(true);
    try {
      const res = await fetch(`${API_URL}/reports/?id_employees=${user.id_employees}`);
      if (res.ok) {
        const data = await res.json();
        setReportsData(data);
      }
    } catch (e) {
      console.error("Error fetching reports:", e);
    } finally {
      setReportsLoading(false);
    }
  };

  // Navigation functions supporting history tracking
  const navigateTo = (view) => {
    setHistory(prev => [...prev, currentView]);
    setCurrentView(view);
    if (view === 'reports' && !reportsData) {
      fetchReports();
    }
  };

  const navigateBack = () => {
    if (history.length > 0) {
      const prev = history[history.length - 1];
      setHistory(prev => prev.slice(0, -1));
      setCurrentView(prev);
    } else {
      setCurrentView('menu');
    }
  };

  // Load persistent login session on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('clinica_user');
    if (savedUser) {
      const parsed = JSON.parse(savedUser);
      setUser(parsed);
      fetchFisioType(parsed.id_employees);
      setCurrentView('menu');
    }
  }, []);

  // Fetch lists whenever user changes or view demands it
  useEffect(() => {
    if (user) {
      if (!patientsFetched) fetchPatients();
      if (!appointmentsFetched) fetchAppointments();
    }
  }, [user]);

  const fetchFisioType = async (employeeId) => {
    try {
      const res = await fetch(`${API_URL}/fisio_type/?id_employees=${employeeId}`);
      if (res.ok) {
        const data = await res.json();
        setFisioType(data.fisio_type || '');
      }
    } catch (e) {
      console.error("Error fetching fisio type:", e);
    }
  };

  const fetchPatients = async () => {
    if (!user) return;
    setPatientsLoading(true);
    try {
      const res = await fetch(`${API_URL}/patients_list/?id_employees=${user.id_employees}`);
      if (res.ok) {
        const data = await res.json();
        setPatients(data || []);
        setPatientsFetched(true);
      }
    } catch (e) {
      console.error("Error fetching patients:", e);
    } finally {
      setPatientsLoading(false);
    }
  };

  const fetchAppointments = async () => {
    if (!user) return;
    setAppointmentsLoading(true);
    try {
      const res = await fetch(`${API_URL}/patients_appointments/?id_employees=${user.id_employees}`);
      if (res.ok) {
        const data = await res.json();
        setAppointments(data || []);
        setAppointmentsFetched(true);
      }
    } catch (e) {
      console.error("Error fetching appointments:", e);
    } finally {
      setAppointmentsLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!usernameInput || !passwordInput) return;

    setAuthLoading(true);
    setAuthError('');

    try {
      const res = await fetch(`${API_URL}/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: usernameInput,
          password: passwordInput
        })
      });

      if (res.ok) {
        const data = await res.json();
        if (data.ok) {
          const loggedInUser = {
            id_employees: data.id_employees,
            username: data.username,
            name: data.name,
            last_name: data.last_name,
            role: data.role,
            profile_picture: data.profile_picture
          };
          setUser(loggedInUser);
          localStorage.setItem('clinica_user', JSON.stringify(loggedInUser));
          
          setPatientsFetched(false);
          setAppointmentsFetched(false);
          fetchFisioType(data.id_employees);
          setHistory([]);
          setCurrentView('menu');
        } else {
          setAuthError('Usuario o contraseña incorrectos.');
        }
      } else {
        setAuthError('Error de servidor en el inicio de sesión.');
      }
    } catch (e) {
      setAuthError('No se pudo conectar con el servidor.');
      console.error(e);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('clinica_user');
    setUser(null);
    setPatients([]);
    setPatientsFetched(false);
    setAppointments([]);
    setAppointmentsFetched(false);
    setFisioType('');
    setUsernameInput('');
    setPasswordInput('');
    setHistory([]);
    setCurrentView('login');
  };

  const handleUploadProfilePicture = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setProfilePictureUploading(true);
    const formData = new FormData();
    formData.append("id_employees", user.id_employees);
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/profile/upload_picture/`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.ok) {
        const updatedUser = { ...user, profile_picture: data.url };
        setUser(updatedUser);
        localStorage.setItem("clinica_user", JSON.stringify(updatedUser));
        showAlert("¡Éxito!", "Foto de perfil actualizada correctamente.", "success");
      } else {
        showAlert("Error", "Error al subir la foto: " + (data.error || ""), "error");
      }
    } catch (err) {
      console.error(err);
      showAlert("Error de Conexión", "No se pudo establecer conexión con el servidor al subir la foto.", "error");
    } finally {
      setProfilePictureUploading(false);
    }
  };
  const submitPatientCreation = async (patientData) => {
    try {
      const res = await fetch(`${API_URL}/add_patients/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData)
      });

      if (res.ok) {
        setNewPatient({
          name: '',
          last_name: '',
          phone: '',
          doctor_sender: '',
          doctor_selected: '',
          instructions: '',
          aseguradora: ''
        });
        setInstructionsText('');
        showAlert('¡Éxito!', 'Paciente registrado exitosamente.', 'success', () => {
          fetchPatients();
          navigateBack();
        });
      } else {
        showAlert('Error', 'Error al registrar el paciente.', 'error');
      }
    } catch (e) {
      console.error(e);
      showAlert('Error de Conexión', 'No se pudo conectar al servidor.', 'error');
    }
  };

  const handleCreatePatient = async (e) => {
    e.preventDefault();
    
    if (fisioType === 'Acuática' && !newPatient.doctor_selected) {
      showAlert('Información', 'Por favor, selecciona una doctora encargada.', 'info');
      return;
    }

    // Validation for duplicate name and phone number
    const cleanPhone = (ph) => String(ph || '').replace(/\D/g, '');
    const nameLower = newPatient.name.trim().toLowerCase();
    const lastNameLower = newPatient.last_name.trim().toLowerCase();
    const newPhoneClean = cleanPhone(newPatient.phone);

    const matchesName = patients.filter(p => 
      p.name.trim().toLowerCase() === nameLower && 
      p.last_name.trim().toLowerCase() === lastNameLower
    );

    const patientData = {
      name: newPatient.name,
      last_name: newPatient.last_name,
      phone: newPatient.phone,
      id_employees: user.id_employees,
      doctor_selected: newPatient.doctor_selected || null,
      instructions: instructionsText || newPatient.instructions,
      aseguradora: newPatient.aseguradora || '',
      doctor_sender: newPatient.doctor_sender || null
    };

    if (matchesName.length > 0) {
      const hasSamePhone = matchesName.some(p => cleanPhone(p.phone) === newPhoneClean);
      if (hasSamePhone) {
        setShowDuplicateBlockDialog(true);
        return;
      } else {
        setPendingPatientData(patientData);
        setShowDuplicateConfirmDialog(true);
        return;
      }
    }

    await submitPatientCreation(patientData);
  };

  const submitSessionCreation = async (sessionData) => {
    try {
      const res = await fetch(`${API_URL}/add_sesion/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sessionData)
      });

      if (res.ok) {
        setNewSession({
          id_patient: '',
          entry_date: new Date().toISOString().split('T')[0],
          entry_time: '09:00:00',
          sesion_type: 'Consulta'
        });
        showAlert('¡Éxito!', 'Sesión agendada correctamente.', 'success', () => {
          fetchAppointments();
          fetchPatients();
          setReportsData(null);
          navigateBack();
        });
      } else {
        showAlert('Error', 'Error al agendar la sesión.', 'error');
      }
    } catch (e) {
      console.error(e);
      showAlert('Error de Conexión', 'No se pudo conectar al servidor.', 'error');
    }
  };
  const handleChangeSessionDate = async () => {
    if (!changeDateSessionId || !changeDateValue || !changeTimeValue) return;
    try {
      const res = await fetch(`${API_URL}/change_session_date/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_sesion: changeDateSessionId,
          entry_date: changeDateValue,
          entry_time: changeTimeValue
        })
      });

      if (res.ok) {
        showAlert('¡Éxito!', 'Fecha de la cita actualizada correctamente.', 'success', () => {
          setShowChangeDateDialog(false);
          fetchAppointments();
          setReportsData(null);
        });
      } else {
        showAlert('Error', 'Error al cambiar la fecha de la cita.', 'error');
      }
    } catch (e) {
      console.error(e);
      showAlert('Error de Conexión', 'No se pudo conectar al servidor.', 'error');
    }
  };

  const handleCreateSession = async (e) => {
    e.preventDefault();
    if (!newSession.id_patient) {
      showAlert('Información', 'Por favor, selecciona un paciente.', 'info');
      return;
    }

    const sessionData = {
      id_patient: parseInt(newSession.id_patient),
      entry_time: newSession.entry_time,
      entry_date: newSession.entry_date,
      sesion_type: newSession.sesion_type,
      id_employees: user.id_employees
    };

    try {
      // Check for collisions first
      const checkRes = await fetch(`${API_URL}/check_collision/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entry_date: newSession.entry_date,
          entry_time: newSession.entry_time,
          sesion_type: newSession.sesion_type
        })
      });

      if (checkRes.ok) {
        const checkData = await checkRes.json();
        if (checkData.collisions && checkData.collisions.length > 0) {
          const collisionList = checkData.collisions.map(c => `${c.name} ${c.last_name} (${c.sesion_type})`).join(', ');
          setCollisionText(collisionList);
          setPendingSessionData(sessionData);
          setShowCollisionDialog(true);
          return;
        }
      }

      // If no collision, submit directly
      await submitSessionCreation(sessionData);
    } catch (e) {
      console.error(e);
      showAlert('Error de Conexión', 'No se pudo conectar al servidor para verificar colisiones.', 'error');
    }
  };

  const handleEditPatient = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/edit_patient_info/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editPatientForm)
      });

      if (res.ok) {
        showAlert('¡Éxito!', 'Información del paciente actualizada.', 'success', () => {
          fetchPatients();
          fetchAppointments();
          navigateBack();
        });
      } else {
        showAlert('Error', 'Error al actualizar la información.', 'error');
      }
    } catch (e) {
      console.error(e);
      showAlert('Error de Conexión', 'No se pudo conectar al servidor.', 'error');
    }
  };

  const handleLoadNotes = async (patientId) => {
    try {
      const res = await fetch(`${API_URL}/show_info/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_patient: patientId
        })
      });
      if (res.ok) {
        const data = await res.json();
        setNotesText(data.info || '');
        setNotesPatientId(patientId);
        setShowNotesDialog(true);
      } else {
        showAlert('Error', 'Error al cargar la información del paciente.', 'error');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSaveNotes = async () => {
    try {
      const res = await fetch(`${API_URL}/update_notes/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_patient: notesPatientId,
          imp_data: notesText
        })
      });
      if (res.ok) {
        setPatients(prev => prev.map(p => {
          if (p.id_patient === notesPatientId) {
            return { ...p, imp_data: notesText };
          }
          return p;
        }));
        setShowNotesDialog(false);
        showAlert('¡Éxito!', 'Asistencia registrada y notas actualizadas correctamente.', 'success');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleOpenConsultationModal = (patientOrAppt) => {
    setConsultationPatient(patientOrAppt);
    setConsultationText('');
    setShowConsultationModal(true);
  };

  const handleExportPdf = async () => {
    if (!consultationPatient || !consultationText.trim()) {
      showAlert('Información', 'Por favor, escribe el contenido de la consulta.', 'info');
      return;
    }
    setExportingPdf(true);
    try {
      const response = await fetch(`${API_URL}/export_pdf/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_patient: consultationPatient.id_patient,
          text: consultationText,
          id_employees: user.id_employees
        })
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `consulta_${consultationPatient.name}_${consultationPatient.last_name}.pdf`.replace(/\s+/g, '_');
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        setShowConsultationModal(false);
      } else {
        showAlert('Error', 'No se pudo generar el PDF de la consulta.', 'error');
      }
    } catch (e) {
      console.error(e);
      showAlert('Error de Conexión', 'No se pudo conectar con el servidor para exportar el PDF.', 'error');
    } finally {
      setExportingPdf(false);
    }
  };

  const submitAttendance = async (attended) => {
    try {
      const res = await fetch(`${API_URL}/asistance/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_sesion: attendanceSessionId,
          asistance: attended
        })
      });
      if (res.ok) {
        showAlert('¡Éxito!', 'Asistencia registrada correctamente.', 'success', () => {
          setShowAttendanceDialog(false);
          fetchAppointments();
          fetchPatients();
          setReportsData(null);
        });
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Filter lists
  const filteredPatients = useMemo(() => {
    if (!patientSearch.trim()) return [];
    return patients.filter(p => {
      const fullname = `${p.name} ${p.last_name}`.toLowerCase();
      const phone = p.phone ? p.phone.toString() : '';
      return fullname.includes(patientSearch.toLowerCase()) || phone.includes(patientSearch);
    });
  }, [patients, patientSearch]);

  const filteredAppointments = useMemo(() => {
    const isSearching = appointmentsSearch.trim() !== '';
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const parseLocalDate = (dateStr) => {
      if (!dateStr) return null;
      const clean = dateStr.split('T')[0];
      const parts = clean.split('-');
      if (parts.length !== 3) return null;
      return new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
    };

    const searched = appointments.filter(a => {
      const fullname = `${a.name} ${a.last_name}`.toLowerCase();
      const phone = a.phone ? a.phone.toString() : '';
      return fullname.includes(appointmentsSearch.toLowerCase()) || phone.includes(appointmentsSearch);
    });

    const activeFilter = isSearching ? 'month' : apptFilter;

    const filtered = searched.filter(a => {
      const apptDate = parseLocalDate(a.entry_date);
      if (!apptDate) return false;

      // Rule 1: If it's already marked as Asistió or No Asistió
      if (a.state === 'Asistió' || a.state === 'No Asistió') {
        // Show ONLY if the user is searching AND it's in the current month
        if (!isSearching) return false;
        const isCurrentMonth = apptDate.getMonth() === today.getMonth() && apptDate.getFullYear() === today.getFullYear();
        return isCurrentMonth;
      }

      // Rule 2: If it's Sin empezar, apply regular filters
      if (activeFilter === 'day') {
        return apptDate.toDateString() === today.toDateString();
      }

      if (activeFilter === 'week') {
        const currentDay = today.getDay();
        const diffToMonday = today.getDate() - currentDay + (currentDay === 0 ? -6 : 1);
        const monday = new Date(today);
        monday.setDate(diffToMonday);
        monday.setHours(0, 0, 0, 0);

        const sunday = new Date(monday);
        sunday.setDate(monday.getDate() + 6);
        sunday.setHours(23, 59, 59, 999);

        return apptDate >= monday && apptDate <= sunday;
      }

      if (activeFilter === 'month') {
        return apptDate.getMonth() === today.getMonth() && apptDate.getFullYear() === today.getFullYear();
      }

      return true;
    });

    const sorted = [...filtered];
    sorted.sort((x, y) => {
      const order = { 'Sin empezar': 1, 'Asistió': 2, 'No Asistió': 3 };
      const orderX = order[x.state] || 99;
      const orderY = order[y.state] || 99;
      return orderX - orderY;
    });

    // Group by entry_date
    const groupsMap = {};
    sorted.forEach(appt => {
      const dateKey = appt.entry_date ? appt.entry_date.split('T')[0] : 'Sin Fecha';
      if (!groupsMap[dateKey]) {
        groupsMap[dateKey] = [];
      }
      groupsMap[dateKey].push(appt);
    });

    // Sort dates by proximity to today
    const sortedDateKeys = Object.keys(groupsMap).sort((a, b) => {
      if (a === 'Sin Fecha') return 1;
      if (b === 'Sin Fecha') return -1;
      const dateA = parseLocalDate(a);
      const dateB = parseLocalDate(b);
      const distA = dateA ? Math.abs(dateA - today) : Infinity;
      const distB = dateB ? Math.abs(dateB - today) : Infinity;
      return distA - distB;
    });

    return sortedDateKeys.map(key => ({
      date: key,
      appts: groupsMap[key]
    }));
  }, [appointments, appointmentsSearch, apptFilter]);

  // Calendar events
  const daysInMonth = useMemo(() => {
    const year = calendarDate.getFullYear();
    const month = calendarDate.getMonth();
    const dateObj = new Date(year, month, 1);
    const days = [];
    
    const firstDayIndex = dateObj.getDay();
    const prevMonthLastDate = new Date(year, month, 0).getDate();
    for (let i = firstDayIndex - 1; i >= 0; i--) {
      days.push({ day: prevMonthLastDate - i, isCurrentMonth: false, date: new Date(year, month - 1, prevMonthLastDate - i) });
    }

    const lastDate = new Date(year, month + 1, 0).getDate();
    for (let i = 1; i <= lastDate; i++) {
      days.push({ day: i, isCurrentMonth: true, date: new Date(year, month, i) });
    }

    return days;
  }, [calendarDate]);

  const getSessionsForDate = (dateObj) => {
    if (!dateObj) return [];
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    const dateString = `${year}-${month}-${day}`;
    
    return appointments.filter(a => {
      if (!a.entry_date) return false;
      if (a.state !== 'Sin empezar') return false;
      const apptDateString = typeof a.entry_date === 'string' ? a.entry_date.split('T')[0] : '';
      return apptDateString === dateString;
    });
  };

  const selectedDaySessions = useMemo(() => {
    return getSessionsForDate(calendarDate);
  }, [calendarDate, appointments]);

  // Path helper for local images
  const getAvatarPath = (name) => {
    if (!name) return '/assets/images/persona.png';
    const formatted = name.trim();
    return `/assets/images/${formatted}.jpg`;
  };

  // --- RENDERS ---

  // 1. LOGIN SCREEN
  if (currentView === 'login') {
    return (
      <div className="app-container">
        <div className="login-wrapper fade-in">
          <div className="login-card">
            <div className="login-illustration-container">
              <img src="/assets/images/login_illustration.png" alt="Rehabilitación" className="login-illustration" />
              <img src="/assets/images/logoSysGesCli.jpg" alt="Logo" className="login-illustration-logo" />
            </div>
            
            <div className="login-content">
              <h1 className="login-title">¡Bienvenido!</h1>
              <p className="login-subtitle">Sistema de Control y Gestión Clínica</p>

              {authError && <div className="login-error-card">{authError}</div>}

              <form onSubmit={handleLogin} className="login-form">
                <label className="login-label">Usuario</label>
                <div className="login-input-wrapper">
                  <User size={18} className="login-input-icon" />
                  <input 
                    type="text" 
                    placeholder="Introduce tu usuario"
                    className="login-input" 
                    value={usernameInput}
                    onChange={(e) => setUsernameInput(e.target.value)}
                    required 
                  />
                </div>

                <label className="login-label">Contraseña</label>
                <div className="login-input-wrapper">
                  <Key size={18} className="login-input-icon" />
                  <input 
                    type={showPassword ? "text" : "password"} 
                    placeholder="Introduce tu contraseña"
                    className="login-input" 
                    value={passwordInput}
                    onChange={(e) => setPasswordInput(e.target.value)}
                    required 
                  />
                  <button 
                    type="button" 
                    className="login-password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  >
                    {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
                  </button>
                </div>

                <div className="forgot-password-link">¿Olvidaste tu contraseña?</div>

                <button type="submit" className="login-btn" disabled={authLoading}>
                  {authLoading ? <div className="spinner"></div> : 'Entrar'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Common Header Card
  const renderHeader = (title, backAction = navigateBack) => {
    if (!user) return null;
    return (
      <div className="header-card">
        <h2 className="header-title">{title}</h2>
        
        <button className="header-back-btn" onClick={backAction}>
          <img src="/assets/images/regreso.png" alt="Regresar" className="header-back-btn-img" />
        </button>

        <div 
          className="header-avatar" 
          onClick={() => {
            if (!profilePictureUploading) {
              setShowOptionsModal(true);
            }
          }}
          style={{ cursor: 'pointer', position: 'relative', overflow: 'hidden', borderRadius: '50%' }}
        >
          <img 
            src={user.profile_picture || '/assets/images/persona.png'} 
            alt="Avatar" 
            className="header-avatar-img" 
            style={{ opacity: profilePictureUploading ? 0.5 : 1, display: 'block' }}
          />
          
          {!profilePictureUploading && (
            <div className="avatar-hover-overlay">
              <Camera size={24} color="white" />
            </div>
          )}

          {profilePictureUploading && (
            <div className="avatar-loading-overlay">
              <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
            </div>
          )}
        </div>

        <div className="header-profile-name">{user.name} {user.last_name}</div>
        <div className="header-profile-role">{user.role}</div>
      </div>
    );
  };

  return (
    <div className="app-container">

      {/* 2. MENU SCREEN */}
      {currentView === 'menu' && (
        <div className="menu-wrapper fade-in">
          {renderHeader('Menu', handleLogout)}
          
          <div className="menu-list">
            <button className="menu-btn" onClick={() => navigateTo('calendar')}>
              <img src="/assets/images/calendario.png" alt="Calendario" className="menu-btn-icon" />
              <span className="menu-btn-text">Calendario Remes</span>
            </button>

            <button className="menu-btn" onClick={() => navigateTo('appointments')}>
              <img src="/assets/images/persona.png" alt="Citas" className="menu-btn-icon" />
              <span className="menu-btn-text">Mis Citas</span>
            </button>

            <button className="menu-btn" onClick={() => navigateTo('add_patient')}>
              <img src="/assets/images/tabla.png" alt="Agregar" className="menu-btn-icon" />
              <span className="menu-btn-text">Agregar pacientes</span>
            </button>

            <button className="menu-btn" onClick={() => navigateTo('all_patients')}>
              <img src="/assets/images/tabla2.png" alt="Todos" className="menu-btn-icon" />
              <span className="menu-btn-text">Todos mis pacientes</span>
            </button>

            <button className="menu-btn" onClick={() => navigateTo('reports')}>
              <img src="/assets/images/historial.png" alt="Registros" className="menu-btn-icon" />
              <span className="menu-btn-text">Registros</span>
            </button>
          </div>
        </div>
      )}

      {/* 3. CALENDAR SCREEN */}
      {currentView === 'calendar' && (
        <div className="list-wrapper fade-in">
          {renderHeader('Calendario Remes')}

          {/* TableCalendar */}
          <div className="calendar-block">
            <div className="calendar-header">
              <button className="calendar-nav-btn" onClick={() => setCalendarDate(new Date(calendarDate.setMonth(calendarDate.getMonth() - 1)))}>
                ◀
              </button>
              <span className="calendar-header-title">
                {calendarDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' }).toUpperCase()}
              </span>
              <button className="calendar-nav-btn" onClick={() => setCalendarDate(new Date(calendarDate.setMonth(calendarDate.getMonth() + 1)))}>
                ▶
              </button>
            </div>

            <div className="calendar-grid-orig">
              {['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'].map(dayName => (
                <div key={dayName} className="calendar-day-header-orig">{dayName}</div>
              ))}

              {daysInMonth.map((dayObj, i) => {
                const daySessions = getSessionsForDate(dayObj.date);
                const isSelected = dayObj.date.toDateString() === calendarDate.toDateString();
                const isToday = dayObj.date.toDateString() === new Date().toDateString();
                const hasEvents = daySessions.length > 0;

                let cellClass = 'calendar-day-cell-orig';
                if (!dayObj.isCurrentMonth) cellClass += ' other-month';
                if (isSelected) cellClass += ' selected';
                else if (hasEvents) cellClass += ' has-events';
                else if (isToday) cellClass += ' today';

                return (
                  <div 
                    key={i} 
                    className={cellClass}
                    onClick={() => setCalendarDate(dayObj.date)}
                  >
                    {dayObj.day}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Selected Day sessions */}
          <div className="list-container" style={{ background: '#f4f6f9', borderTop: '1px solid #e0e0e0' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 'bold', margin: '8px 0' }}>
              Sesiones para el {calendarDate.getDate()}/{calendarDate.getMonth() + 1}/{calendarDate.getFullYear()}
            </h3>

            {selectedDaySessions.length === 0 ? (
              <p style={{ color: '#555555', textAlign: 'center', marginTop: '16px' }}>No hay sesiones en este día</p>
            ) : (
              selectedDaySessions.map(session => (
                <div key={session.id_sesion} className="patient-card">
                  <div className="patient-card-icon">
                    <img src="/assets/images/persona.png" alt="Paciente" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                  </div>
                  <div className="patient-card-content">
                    <span className="patient-card-title">{session.name} {session.last_name}</span>
                    <span className="patient-card-detail">Hora: {session.entry_time}</span>
                    <span className="patient-card-detail">Teléfono: {session.phone}</span>
                    <span className="patient-card-detail">Pago: ${session.amount_to_pay}</span>
                    <span className="patient-card-detail">
                      Tipo de sesión: <span className={`session-badge session-badge-${session.sesion_type ? session.sesion_type.toLowerCase() : ''}`}>{getSessionDisplayText(session.sesion_type, session.doctor_charge)}</span>
                    </span>
                    {session.aseguradora && (
                      <span className="patient-card-detail">Aseguradora: {session.aseguradora}</span>
                    )}
                    <span className="patient-card-detail"><strong>Estado: {session.state}</strong></span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* 4. MIS CITAS SCREEN */}
      {currentView === 'appointments' && (
        <div className="list-wrapper fade-in">
          {renderHeader('Mis citas')}

          <div className="list-container">
            <div className="search-bar-container">
              <Search size={18} className="search-bar-icon" />
              <input 
                type="text" 
                placeholder="Buscar paciente..." 
                className="search-bar"
                value={appointmentsSearch}
                onChange={(e) => {
                  const val = e.target.value;
                  setAppointmentsSearch(val);
                  if (val.trim() !== '') {
                    setApptFilter('month');
                  }
                }}
              />
            </div>

            <div className="filter-tabs">
              {appointmentsSearch.trim() === '' ? (
                <>
                  <button 
                    type="button"
                    className={`filter-tab ${apptFilter === 'day' ? 'active' : ''}`}
                    onClick={() => setApptFilter('day')}
                  >
                    Día
                  </button>
                  <button 
                    type="button"
                    className={`filter-tab ${apptFilter === 'week' ? 'active' : ''}`}
                    onClick={() => setApptFilter('week')}
                  >
                    Semana
                  </button>
                  <button 
                    type="button"
                    className={`filter-tab ${apptFilter === 'month' ? 'active' : ''}`}
                    onClick={() => setApptFilter('month')}
                  >
                    Mes
                  </button>
                </>
              ) : (
                <button 
                  type="button"
                  className="filter-tab active"
                  style={{ cursor: 'default' }}
                >
                  Mes
                </button>
              )}
            </div>

            {appointmentsLoading ? (
              <p style={{ textAlign: 'center', color: '#555555' }}>Cargando citas...</p>
            ) : filteredAppointments.length === 0 ? (
              <p style={{ textAlign: 'center', color: '#555555' }}>No hay citas registradas</p>
            ) : (
              filteredAppointments.map(group => (
                <div key={group.date} style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                  <div className="date-group-header">
                    {group.date === 'Sin Fecha' ? 'Sin Fecha' : formatSessionDate(group.date)}
                  </div>
                  {group.appts.map(appt => (
                    <div key={appt.id_sesion} className="patient-card" style={{ marginBottom: '12px' }}>
                      <div className="patient-card-icon">
                        <img src="/assets/images/persona.png" alt="Paciente" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                      </div>
                      <div className="patient-card-content">
                        <span className="patient-card-title">{appt.name} {appt.last_name}</span>
                        <span className="patient-card-detail">Fecha de consulta: {formatSessionDate(appt.entry_date)}</span>
                        <span className="patient-card-detail">Hora: {appt.entry_time}</span>
                        <span className="patient-card-detail">Teléfono: {appt.phone}</span>
                        <span className="patient-card-detail">Pago: ${appt.amount_to_pay}</span>
                        <span className="patient-card-detail">
                          Tipo de sesión: <span className={`session-badge session-badge-${appt.sesion_type ? appt.sesion_type.toLowerCase() : ''}`}>{getSessionDisplayText(appt.sesion_type, appt.doctor_charge)}</span>
                        </span>
                        {appt.aseguradora && (
                          <span className="patient-card-detail">Aseguradora: {appt.aseguradora}</span>
                        )}
                        {appt.state && appt.state !== 'Sin empezar' && (
                          <span className="patient-card-detail"><strong>Estado: {appt.state}</strong></span>
                        )}
                        
                        <div style={{ marginTop: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                          {appt.state === 'Sin empezar' && 
                            !(user && user.id_employees === 9 && appt.sesion_type !== 'Alberca') && (
                              <>
                                <button 
                                  className="pill-btn pill-btn-small"
                                  onClick={() => {
                                    setAttendanceSessionId(appt.id_sesion);
                                    setShowAttendanceDialog(true);
                                  }}
                                >
                                  Registrar asistencia
                                </button>
                                <button 
                                  type="button"
                                  className="pill-btn pill-btn-small pill-btn-danger"
                                  onClick={() => {
                                    setChangeDateSessionId(appt.id_sesion);
                                    setChangeDateValue(appt.entry_date ? appt.entry_date.split('T')[0] : '');
                                    setChangeTimeValue(appt.entry_time || '09:00:00');
                                    setShowChangeDateDialog(true);
                                  }}
                                >
                                  Cambiar fecha
                                </button>
                              </>
                            )
                          }
                          <button 
                            className="pill-btn pill-btn-small"
                            onClick={() => handleOpenConsultationModal(appt)}
                          >
                            Consulta
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* 5. AGREGAR PACIENTES SCREEN */}
      {currentView === 'add_patient' && (
        <div className="form-wrapper fade-in">
          {renderHeader('Agregar pacientes')}

          <form onSubmit={handleCreatePatient} className="form-container">
            <label className="form-label">Nombre</label>
            <input 
              type="text" 
              className="form-input" 
              value={newPatient.name}
              onChange={(e) => setNewPatient({ ...newPatient, name: e.target.value })}
              required 
            />

            <label className="form-label">Apellido</label>
            <input 
              type="text" 
              className="form-input" 
              value={newPatient.last_name}
              onChange={(e) => setNewPatient({ ...newPatient, last_name: e.target.value })}
              required 
            />

            <label className="form-label">Teléfono</label>
            <input 
              type="text" 
              className="form-input" 
              value={newPatient.phone}
              onChange={(e) => setNewPatient({ ...newPatient, phone: e.target.value })}
              required 
            />

            <label className="form-label">Doctor que envía</label>
            <input 
              type="text" 
              className="form-input" 
              value={newPatient.doctor_sender}
              onChange={(e) => setNewPatient({ ...newPatient, doctor_sender: e.target.value })}
            />

            <label className="form-label">Aseguradora</label>
            <input 
              type="text" 
              className="form-input" 
              value={newPatient.aseguradora}
              onChange={(e) => setNewPatient({ ...newPatient, aseguradora: e.target.value })}
            />

            {fisioType === 'Acuática' && (
              <>
                <label className="form-label">Selecciona doctora</label>
                <select 
                  className="form-select"
                  value={newPatient.doctor_selected}
                  onChange={(e) => setNewPatient({ ...newPatient, doctor_selected: e.target.value })}
                  required
                >
                  <option value="">-- Selecciona Encargada --</option>
                  <option value="Gabriela">Dra. Gabriela</option>
                  <option value="Valeria">Dra. Valeria</option>
                </select>
              </>
            )}

            <div className="btn-row">
              <button 
                type="button" 
                className="btn-instructions"
                onClick={() => setShowInstructionsModal(true)}
              >
                Instrucciones
              </button>
              
              <button type="submit" className="btn-save">
                <img src="/assets/images/regreso.png" alt="Guardar" className="btn-save-img" />
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 6. TODOS MIS PACIENTES SCREEN */}
      {currentView === 'all_patients' && (
        <div className="list-wrapper fade-in">
          {renderHeader('Todos mis pacientes')}

          <div className="list-container">
            <div className="search-bar-container">
              <Search size={18} className="search-bar-icon" />
              <input 
                type="text" 
                placeholder="Buscar paciente..." 
                className="search-bar"
                value={patientSearch}
                onChange={(e) => setPatientSearch(e.target.value)}
              />
            </div>

            {patientsLoading ? (
              <p style={{ textAlign: 'center', color: '#555555' }}>Cargando pacientes...</p>
            ) : !patientSearch.trim() ? (
              <p style={{ textAlign: 'center', color: '#64748b', marginTop: '32px', fontSize: '15px', fontWeight: '500' }}>Busque a su paciente</p>
            ) : filteredPatients.length === 0 ? (
              <p style={{ textAlign: 'center', color: '#555555' }}>No se encontraron pacientes</p>
            ) : (
              filteredPatients.map(p => (
                <div key={p.id_patient} className="patient-card">
                  <div className="patient-card-icon">
                    <img src="/assets/images/persona.png" alt="Paciente" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                  </div>
                  <div className="patient-card-content">
                    <span className="patient-card-title">{p.name} {p.last_name}</span>
                    <span className="patient-card-detail">Teléfono: {p.phone}</span>
                    {p.doctor_sender && (
                      <span className="patient-card-detail">Doctor que envía: {p.doctor_sender}</span>
                    )}
                    <span className="patient-card-detail">Pago: ${p.amount_to_pay}</span>
                    {p.aseguradora && (
                      <span className="patient-card-detail">Aseguradora: {p.aseguradora}</span>
                    )}
                    
                    <div className="patient-card-buttons">
                      <button 
                        className="pill-btn pill-btn-small"
                        onClick={() => handleLoadNotes(p.id_patient)}
                      >
                        Notas
                      </button>

                      <button 
                        className="pill-btn pill-btn-small"
                        onClick={() => {
                          setNewSession(prev => ({ ...prev, id_patient: p.id_patient }));
                          navigateTo('add_session');
                        }}
                      >
                        Sesión
                      </button>

                      <button 
                        className="pill-btn pill-btn-small"
                        onClick={() => {
                          setEditPatientForm({
                            id_patient: p.id_patient,
                            name: p.name,
                            last_name: p.last_name,
                            phone: p.phone,
                            doctor_sender: p.doctor_sender || '',
                            amount_to_pay: p.amount_to_pay
                          });
                          navigateTo('edit_patient_info');
                        }}
                      >
                        Editar
                      </button>

                      <button 
                        className="pill-btn pill-btn-small"
                        onClick={() => handleOpenConsultationModal(p)}
                      >
                        Consulta
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* 7. AGREGAR CITA SCREEN */}
      {currentView === 'add_session' && (
        <div className="form-wrapper fade-in">
          {renderHeader('Agregar Cita')}

          <form onSubmit={handleCreateSession} className="form-container">
            <label className="form-label">Fecha de cita</label>
            <input 
              type="date" 
              className="form-input" 
              value={newSession.entry_date}
              onChange={(e) => setNewSession({ ...newSession, entry_date: e.target.value })}
              required 
            />

            <label className="form-label">Tipo de sesión</label>
            <select 
              className="form-select"
              value={newSession.sesion_type}
              onChange={(e) => setNewSession({ ...newSession, sesion_type: e.target.value })}
              required
            >
              <option value="Consulta">Consulta ($800)</option>
              <option value="Terapia">Terapia ($350)</option>
              <option value="Alberca">Alberca ($400)</option>
            </select>

            <label className="form-label">Hora (HH:MM:SS)</label>
            <input 
              type="time" 
              step="1"
              className="form-input" 
              value={newSession.entry_time}
              onChange={(e) => {
                let val = e.target.value;
                if (val.length === 5) val += ':00';
                setNewSession({ ...newSession, entry_time: val });
              }}
              required 
            />

            <div className="btn-row">
              <button type="submit" className="btn-save">
                <img src="/assets/images/regreso.png" alt="Guardar" className="btn-save-img" />
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 8. EDIT PATIENT INFO SCREEN */}
      {currentView === 'edit_patient_info' && (
        <div className="form-wrapper fade-in">
          {renderHeader('Editar Información')}

          <form onSubmit={handleEditPatient} className="form-container">
            <label className="form-label">Nombre</label>
            <input 
              type="text" 
              className="form-input" 
              value={editPatientForm.name}
              onChange={(e) => setEditPatientForm({ ...editPatientForm, name: e.target.value })}
              required 
            />

            <label className="form-label">Apellido</label>
            <input 
              type="text" 
              className="form-input" 
              value={editPatientForm.last_name}
              onChange={(e) => setEditPatientForm({ ...editPatientForm, last_name: e.target.value })}
              required 
            />

            <label className="form-label">Teléfono</label>
            <input 
              type="text" 
              className="form-input" 
              value={editPatientForm.phone}
              onChange={(e) => setEditPatientForm({ ...editPatientForm, phone: e.target.value })}
              required 
            />

            <label className="form-label">Doctor que envía</label>
            <input 
              type="text" 
              className="form-input" 
              value={editPatientForm.doctor_sender}
              onChange={(e) => setEditPatientForm({ ...editPatientForm, doctor_sender: e.target.value })}
            />

            <label className="form-label">Adeudo Actual ($)</label>
            <input 
              type="number" 
              className="form-input" 
              value={editPatientForm.amount_to_pay}
              onChange={(e) => setEditPatientForm({ ...editPatientForm, amount_to_pay: parseInt(e.target.value) || 0 })}
              required 
            />

            <div className="btn-row">
              <button type="submit" className="btn-save">
                <img src="/assets/images/regreso.png" alt="Guardar" className="btn-save-img" />
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 9. REGISTROS / REPORTS SCREEN */}
      {currentView === 'reports' && (
        <div className="list-wrapper fade-in">
          {renderHeader('Registros')}

          <div className="list-container">
            <div className="filter-tabs" style={{ marginBottom: '20px' }}>
              <button 
                type="button"
                className={`filter-tab ${reportFilter === 'week' ? 'active' : ''}`}
                onClick={() => setReportFilter('week')}
              >
                Semana
              </button>
              <button 
                type="button"
                className={`filter-tab ${reportFilter === 'month' ? 'active' : ''}`}
                onClick={() => setReportFilter('month')}
              >
                Mes
              </button>
              <button 
                type="button"
                className={`filter-tab ${reportFilter === 'year' ? 'active' : ''}`}
                onClick={() => setReportFilter('year')}
              >
                Año
              </button>
            </div>

            {reportsLoading ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '200px', gap: '12px' }}>
                <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '4px', color: '#03175a' }}></div>
                <p style={{ color: '#64748b', fontWeight: '600' }}>Cargando registros...</p>
              </div>
            ) : !reportsData ? (
              <p style={{ textAlign: 'center', color: '#555555', marginTop: '32px' }}>No se pudieron cargar los registros</p>
            ) : (() => {
              // ── Attendance donut ──────────────────────────────────────────
              const asistio   = reportsData[reportFilter].states["Asistió"]    || 0;
              const falto     = reportsData[reportFilter].states["No Asistió"] || 0;
              const pendiente = reportsData[reportFilter].states["Sin empezar"] || 0;
              const totalStates = asistio + falto + pendiente;
              let asistioDeg = 0, faltoDeg = 0;
              if (totalStates > 0) {
                asistioDeg = (asistio   / totalStates) * 360;
                faltoDeg   = (falto     / totalStates) * 360;
              }
              const a1 = asistioDeg, a2 = asistioDeg + faltoDeg;
              const attendanceDonut = totalStates > 0 ? {
                background: `conic-gradient(
                  #166534 0deg, #22c55e ${(a1*0.7).toFixed(1)}deg, #15803d ${a1}deg,
                  #7f1d1d ${a1}deg, #ef4444 ${(a1+(a2-a1)*0.6).toFixed(1)}deg, #b91c1c ${a2}deg,
                  #78350f ${a2}deg, #f59e0b ${(a2+(360-a2)*0.5).toFixed(1)}deg, #d97706 360deg)`
              } : { background: 'linear-gradient(135deg,#cbd5e1,#94a3b8)' };

              // ── Type donut (per doctor) ───────────────────────────────────
              const TYPE_COLORS = [
                ['#1e3a8a','#3b82f6','#1d4ed8'],
                ['#065f46','#10b981','#047857'],
                ['#7c2d12','#f97316','#c2410c'],
                ['#4a044e','#d946ef','#86198f'],
                ['#1e1b4b','#818cf8','#4338ca'],
              ];
              // Static mapping: all doctors that belong to each session type
              const TYPE_DOCTORS = {
                'Consulta': ['Carmen', 'Ana'],
                'Terapia':  ['Hugo', 'Monica'],
                'Alberca':  ['Cristian'],
              };
              const rawByDoc = (reportsData[reportFilter].by_doctor || {})[typeFilter] || [];
              const rawMap = Object.fromEntries(rawByDoc.map(d => [d.name, d.count]));
              // Always show all expected doctors, fill 0 if no sessions
              const byDoc = (TYPE_DOCTORS[typeFilter] || []).map(name => ({
                name,
                count: rawMap[name] || 0
              }));
              const totalDoc = byDoc.reduce((s, d) => s + d.count, 0);
              const typeDonut = (() => {
                if (totalDoc === 0) return { background: 'linear-gradient(135deg,#cbd5e1,#94a3b8)' };
                let deg = 0;
                const stops = [];
                byDoc.forEach((doc, i) => {
                  const [dark, light, mid] = TYPE_COLORS[i % TYPE_COLORS.length];
                  const span = (doc.count / totalDoc) * 360;
                  if (span === 0) return; // skip zero-count to avoid zero-deg segments
                  stops.push(`${dark} ${deg.toFixed(1)}deg`);
                  stops.push(`${light} ${(deg + span*0.55).toFixed(1)}deg`);
                  stops.push(`${mid}  ${(deg + span).toFixed(1)}deg`);
                  deg += span;
                });
                return { background: `conic-gradient(${stops.join(',')})` };
              })();

              return (
                <div className="bi-card fade-in" key={reportFilter}>
                  <div className="bi-card-header">
                    <span className="bi-card-title">
                      {reportFilter === 'week' ? 'Esta Semana' : reportFilter === 'month' ? 'Este Mes' : 'Este Año'}
                    </span>
                    <span className="bi-card-total-badge">
                      {reportsData[reportFilter].total} Citas
                    </span>
                  </div>

                  <div className="bi-card-content">
                    {/* ── Section 1: Tipo con gráfica por doctor ─────────── */}
                    <h4 className="bi-section-title">Distribución por Tipo</h4>

                    {/* Type selector tabs */}
                    <div className="filter-tabs" style={{ marginBottom: '16px' }}>
                      {['Consulta','Terapia','Alberca'].map(t => (
                        <button
                          key={t}
                          type="button"
                          className={`filter-tab ${typeFilter === t ? 'active' : ''}`}
                          onClick={() => setTypeFilter(t)}
                        >{t}</button>
                      ))}
                    </div>

                    {/* Type donut */}
                    <div className="bi-chart-container">
                      <div className="bi-donut-chart" style={typeDonut}>
                        <div className="bi-donut-center">
                          <span className="bi-donut-center-value">{totalDoc}</span>
                          <span className="bi-donut-center-label">{typeFilter}</span>
                        </div>
                      </div>
                    </div>

                    {/* Doctor legend – always shows all expected doctors */}
                    <div className="bi-grid" style={{ gridTemplateColumns: `repeat(${byDoc.length}, 1fr)` }}>
                      {byDoc.map((doc, i) => (
                        <div key={doc.name} className="bi-stat-box" style={{
                          borderColor: TYPE_COLORS[i % TYPE_COLORS.length][1],
                          background: `${TYPE_COLORS[i % TYPE_COLORS.length][1]}18`,
                          opacity: doc.count === 0 ? 0.5 : 1
                        }}>
                          <span className="bi-stat-value" style={{ color: TYPE_COLORS[i % TYPE_COLORS.length][0] }}>{doc.count}</span>
                          <span className="bi-stat-label">{doc.name}</span>
                        </div>
                      ))}
                    </div>

                    {/* ── Section 2: Estado de Asistencia ───────────────── */}
                    <h4 className="bi-section-title" style={{ marginTop: '8px' }}>Estado de Asistencia</h4>
                    <div className="bi-chart-container">
                      <div className="bi-donut-chart" style={attendanceDonut}>
                        <div className="bi-donut-center">
                          <span className="bi-donut-center-value">{totalStates}</span>
                          <span className="bi-donut-center-label">Total</span>
                        </div>
                      </div>
                    </div>
                    <div className="bi-grid">
                      <div className="bi-stat-box asistencia">
                        <span className="bi-stat-value">{asistio}</span>
                        <span className="bi-stat-label">Asistió</span>
                      </div>
                      <div className="bi-stat-box inasistencia">
                        <span className="bi-stat-value">{falto}</span>
                        <span className="bi-stat-label">Faltó</span>
                      </div>
                      <div className="bi-stat-box pendiente">
                        <span className="bi-stat-value">{pendiente}</span>
                        <span className="bi-stat-label">Pendiente</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {/* --- POPUPS / DIALOGS --- */}

      {/* A. ATTENDANCE DIALOG (Asistencia) */}
      {showAttendanceDialog && (
        <div className="dialog-overlay">
          <div className="dialog-box">
            <h3 className="dialog-title">Asistencia</h3>
            <p className="dialog-content">¿El paciente asistió a la sesión?</p>
            <div className="dialog-actions">
              <button className="dialog-btn-text" onClick={() => submitAttendance(false)}>No</button>
              <button className="dialog-btn-primary" onClick={() => submitAttendance(true)}>Sí</button>
            </div>
          </div>
        </div>
      )}

      {/* B. NOTES DIALOG (Notas/Historial) */}
      {showNotesDialog && (
        <div className="dialog-overlay">
          <div className="dialog-box" style={{ maxWidth: '360px' }}>
            <h3 className="dialog-title">Notas / Instrucciones</h3>
            <textarea 
              className="form-input" 
              style={{ width: '100%', minHeight: '120px', textAlign: 'left', padding: '10px', marginBottom: '16px' }}
              value={notesText}
              onChange={(e) => setNotesText(e.target.value)}
            />
            <div className="dialog-actions">
              <button className="dialog-btn-text" onClick={() => setShowNotesDialog(false)}>Cancelar</button>
              <button className="dialog-btn-primary" onClick={handleSaveNotes}>Guardar</button>
            </div>
          </div>
        </div>
      )}

      {/* C. INSTRUCTIONS MODAL (Formulario de Agregar Paciente) */}
      {showInstructionsModal && (
        <div className="dialog-overlay">
          <div className="dialog-box" style={{ maxWidth: '360px' }}>
            <h3 className="dialog-title">Instrucciones del Paciente</h3>
            <textarea 
              className="form-input" 
              style={{ width: '100%', minHeight: '120px', textAlign: 'left', padding: '10px', marginBottom: '16px' }}
              value={instructionsText}
              onChange={(e) => setInstructionsText(e.target.value)}
              placeholder="Instrucciones médicas iniciales..."
            />
            <div className="dialog-actions">
              <button className="dialog-btn-primary" onClick={() => setShowInstructionsModal(false)}>Aceptar</button>
            </div>
          </div>
        </div>
      )}

      {/* D. CONSULTATION PDF DIALOG */}
      {showConsultationModal && consultationPatient && (
        <div className="dialog-overlay">
          <div className="dialog-box" style={{ maxWidth: '450px', width: '90%' }}>
            <h3 className="dialog-title">Nota de Consulta</h3>
            <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '12px' }}>
              Paciente: <strong>{consultationPatient.name} {consultationPatient.last_name}</strong>
            </p>
            <textarea 
              className="form-input" 
              style={{ width: '100%', minHeight: '180px', textAlign: 'left', padding: '10px', marginBottom: '16px', fontSize: '14px', lineHeight: '1.5' }}
              value={consultationText}
              onChange={(e) => setConsultationText(e.target.value)}
              placeholder="Escribe la valoración de la consulta o prescripción médica aquí..."
              disabled={exportingPdf}
            />
            <div className="dialog-actions">
              <button 
                className="dialog-btn-text" 
                onClick={() => setShowConsultationModal(false)}
                disabled={exportingPdf}
              >
                Cancelar
              </button>
              <button 
                className="dialog-btn-primary" 
                onClick={handleExportPdf}
                disabled={exportingPdf || !consultationText.trim()}
              >
                {exportingPdf ? 'Generando...' : 'Exportar a PDF'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* E. COLLISION CONFIRMATION MODAL */}
      {showCollisionDialog && (
        <div className="dialog-overlay">
          <div className="dialog-box" style={{ maxWidth: '380px', padding: '0', overflow: 'hidden' }}>
            <div style={{
              background: 'linear-gradient(135deg, #03175a 0%, #1e5c78 100%)',
              padding: '16px 20px',
              color: '#ffffff'
            }}>
              <h3 className="dialog-title" style={{ color: '#ffffff', margin: '0', fontSize: '18px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
                ⚠️ Conflicto de Cita
              </h3>
            </div>
            <div style={{ padding: '20px' }}>
              <p className="dialog-content" style={{ marginBottom: '20px' }}>
                <strong>¿ESTÁS SEGURO QUE QUIERES AGREGAR?</strong>
                <br/><br/>
                A esta hora está:
                <br/>
                <span style={{ color: '#03175a', fontWeight: 'bold' }}>{collisionText}</span>
              </p>
              <div className="dialog-actions">
                <button 
                  type="button"
                  className="dialog-btn-text" 
                  onClick={() => {
                    setShowCollisionDialog(false);
                    setPendingSessionData(null);
                  }}
                >
                  Cancelar
                </button>
                <button 
                  type="button"
                  className="dialog-btn-primary" 
                  style={{
                    background: 'linear-gradient(135deg, #03175a 0%, #1e5c78 100%)',
                    border: 'none',
                    boxShadow: '0 4px 6px rgba(3, 23, 90, 0.2)'
                  }}
                  onClick={() => {
                    setShowCollisionDialog(false);
                    if (pendingSessionData) {
                      submitSessionCreation(pendingSessionData);
                      setPendingSessionData(null);
                    }
                  }}
                >
                  Sí, agregar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* E. DUPLICATE BLOCK MODAL */}
      {showDuplicateBlockDialog && (
        <div className="dialog-overlay">
          <div className="dialog-box" style={{ maxWidth: '380px', padding: '0', overflow: 'hidden' }}>
            <div style={{
              background: 'linear-gradient(135deg, #7f1d1d 0%, #b91c1c 100%)',
              padding: '16px 20px',
              color: '#ffffff'
            }}>
              <h3 className="dialog-title" style={{ color: '#ffffff', margin: '0', fontSize: '18px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
                ⚠️ Registro No Permitido
              </h3>
            </div>
            <div style={{ padding: '20px' }}>
              <p className="dialog-content" style={{ marginBottom: '20px', fontWeight: '600', color: '#7f1d1d', textAlign: 'center', fontSize: '16px' }}>
                NO SE PUDO
              </p>
              <p className="dialog-content" style={{ marginBottom: '20px', textAlign: 'center', color: '#555555' }}>
                Ya existe un paciente con el mismo nombre y número de teléfono.
              </p>
              <div className="dialog-actions" style={{ justifyContent: 'center' }}>
                <button 
                  type="button"
                  className="dialog-btn-primary" 
                  style={{
                    background: 'linear-gradient(135deg, #7f1d1d 0%, #b91c1c 100%)',
                    border: 'none',
                    boxShadow: '0 4px 6px rgba(185, 28, 28, 0.2)'
                  }}
                  onClick={() => setShowDuplicateBlockDialog(false)}
                >
                  Aceptar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* F. DUPLICATE CONFIRMATION MODAL */}
      {showDuplicateConfirmDialog && (
        <div className="dialog-overlay">
          <div className="dialog-box" style={{ maxWidth: '380px', padding: '0', overflow: 'hidden' }}>
            <div style={{
              background: 'linear-gradient(135deg, #d97706 0%, #f59e0b 100%)',
              padding: '16px 20px',
              color: '#ffffff'
            }}>
              <h3 className="dialog-title" style={{ color: '#ffffff', margin: '0', fontSize: '18px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
                ⚠️ Paciente Registrado
              </h3>
            </div>
            <div style={{ padding: '20px' }}>
              <p className="dialog-content" style={{ marginBottom: '20px', fontWeight: '600', color: '#78350f', textAlign: 'center' }}>
                ESTE USUARIO YA ESTÁ AGREGADO CON OTRO NUMERO ¿DESEAS CONTINUAR?
              </p>
              <div className="dialog-actions">
                <button 
                  type="button"
                  className="dialog-btn-text" 
                  onClick={() => {
                    setShowDuplicateConfirmDialog(false);
                    setPendingPatientData(null);
                  }}
                >
                  Cancelar
                </button>
                <button 
                  type="button"
                  className="dialog-btn-primary" 
                  style={{
                    background: 'linear-gradient(135deg, #d97706 0%, #f59e0b 100%)',
                    border: 'none',
                    boxShadow: '0 4px 6px rgba(217, 119, 6, 0.2)'
                  }}
                  onClick={() => {
                    setShowDuplicateConfirmDialog(false);
                    if (pendingPatientData) {
                      submitPatientCreation(pendingPatientData);
                      setPendingPatientData(null);
                    }
                  }}
                >
                  Sí, continuar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* G. CHANGE SESSION DATE MODAL */}
      {showChangeDateDialog && (
        <div className="dialog-overlay">
          <div className="dialog-box" style={{ maxWidth: '360px' }}>
            <h3 className="dialog-title">Cambiar Fecha / Hora</h3>
            
            <label className="form-label" style={{ marginTop: '10px' }}>Nueva Fecha</label>
            <input 
              type="date" 
              className="form-input" 
              style={{ width: '100%' }}
              value={changeDateValue}
              onChange={(e) => setChangeDateValue(e.target.value)}
              required 
            />

            <label className="form-label" style={{ marginTop: '14px' }}>Nueva Hora</label>
            <input 
              type="time" 
              step="1"
              className="form-input" 
              style={{ width: '100%', marginBottom: '20px' }}
              value={changeTimeValue}
              onChange={(e) => {
                let val = e.target.value;
                if (val.length === 5) val += ':00';
                setChangeTimeValue(val);
              }}
              required 
            />

            <div className="dialog-actions">
              <button 
                type="button" 
                className="dialog-btn-text" 
                onClick={() => setShowChangeDateDialog(false)}
              >
                Cancelar
              </button>
              <button 
                type="button" 
                className="dialog-btn-primary" 
                style={{
                  background: 'linear-gradient(135deg, #03175a 0%, #1e5c78 100%)',
                  border: 'none'
                }}
                onClick={handleChangeSessionDate}
              >
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* H. CUSTOM ALERT MODAL */}
      {modalAlert.show && (
        <div className="dialog-overlay" style={{ zIndex: 1100 }}>
          <div className="dialog-box" style={{ 
            maxWidth: '380px', 
            padding: '0', 
            overflow: 'hidden',
            border: 'none',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)' 
          }}>
            <div style={{
              background: modalAlert.type === 'success' 
                ? 'linear-gradient(135deg, #059669 0%, #10b981 100%)' 
                : modalAlert.type === 'error'
                ? 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)'
                : 'linear-gradient(135deg, #03175a 0%, #1e5c78 100%)',
              padding: '24px 20px',
              color: '#ffffff',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '12px'
            }}>
              {modalAlert.type === 'success' ? (
                <CheckCircle2 size={48} strokeWidth={2} style={{ filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.15))' }} />
              ) : modalAlert.type === 'error' ? (
                <AlertCircle size={48} strokeWidth={2} style={{ filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.15))' }} />
              ) : (
                <Info size={48} strokeWidth={2} style={{ filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.15))' }} />
              )}
              <h3 style={{ 
                color: '#ffffff', 
                margin: '0', 
                fontSize: '19px', 
                fontWeight: '700', 
                textAlign: 'center',
                letterSpacing: '-0.3px'
              }}>
                {modalAlert.title}
              </h3>
            </div>
            <div style={{ padding: '24px 20px', textAlign: 'center' }}>
              <p className="dialog-content" style={{ 
                marginBottom: '24px', 
                color: '#4b5563', 
                fontSize: '15px',
                fontWeight: '500',
                lineHeight: '1.6'
              }}>
                {modalAlert.message}
              </p>
              <div className="dialog-actions" style={{ justifyContent: 'center' }}>
                <button 
                  type="button"
                  className="dialog-btn-primary" 
                  style={{
                    background: modalAlert.type === 'success' 
                      ? 'linear-gradient(135deg, #059669 0%, #10b981 100%)' 
                      : modalAlert.type === 'error'
                      ? 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)'
                      : 'linear-gradient(135deg, #03175a 0%, #1e5c78 100%)',
                    border: 'none',
                    minWidth: '120px',
                    padding: '10px 24px',
                    fontSize: '15px',
                    boxShadow: modalAlert.type === 'success'
                      ? '0 4px 12px rgba(16, 185, 129, 0.3)'
                      : modalAlert.type === 'error'
                      ? '0 4px 12px rgba(239, 68, 68, 0.3)'
                      : '0 4px 12px rgba(3, 23, 90, 0.3)'
                  }}
                  onClick={() => {
                    setModalAlert(prev => ({ ...prev, show: false }));
                    if (modalAlert.onConfirm) {
                      modalAlert.onConfirm();
                    }
                  }}
                >
                  Aceptar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hidden File Input for selecting profile picture */}
      <input 
        type="file" 
        accept="image/*" 
        ref={fileInputRef} 
        style={{ display: 'none' }} 
        onChange={handleSelectFile}
      />

      {/* WhatsApp-style Bottom Sheet Options Menu */}
      {showOptionsModal && (
        <div className="dialog-overlay" onClick={() => setShowOptionsModal(false)} style={{ zIndex: 1150 }}>
          <div 
            className="bottom-sheet" 
            onClick={(e) => e.stopPropagation()} 
          >
            {/* Title Header */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '20px 24px 12px 24px',
              borderBottom: '1px solid rgba(255, 255, 255, 0.08)'
            }}>
              <h3 style={{ 
                color: '#ffffff', 
                margin: '0', 
                fontSize: '18px', 
                fontWeight: '700' 
              }}>
                Edita la foto del perfil
              </h3>
              <button 
                type="button" 
                onClick={() => setShowOptionsModal(false)}
                style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: 'none',
                  borderRadius: '50%',
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                  cursor: 'pointer'
                }}
              >
                <X size={18} />
              </button>
            </div>

            {/* List options */}
            <div style={{ padding: '12px 16px 24px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              
              <button 
                type="button"
                className="bottom-sheet-option"
                onClick={handleCameraOption}
              >
                <Camera size={22} color="#2790b0" />
                <span>Tomar foto</span>
              </button>

              <button 
                type="button"
                className="bottom-sheet-option"
                onClick={() => {
                  fileInputRef.current.click();
                }}
              >
                <Image size={22} color="#2790b0" />
                <span>Seleccionar foto</span>
              </button>

              {user.profile_picture && (
                <button 
                  type="button"
                  className="bottom-sheet-option bottom-sheet-option-danger"
                  onClick={handleDeleteProfilePicture}
                >
                  <Trash2 size={22} color="#ef4444" />
                  <span>Eliminar foto</span>
                </button>
              )}

            </div>
          </div>
        </div>
      )}

      {/* Camera modal */}
      {showCameraModal && (
        <div className="dialog-overlay" style={{ background: '#02071f', zIndex: 1200, padding: '0', flexDirection: 'column' }}>
          {/* Header */}
          <div style={{
            width: '100%',
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #03175a 0%, #1e5c78 100%)',
            color: '#ffffff',
            position: 'relative',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: 30
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '700', letterSpacing: '0.5px' }}>Tomar foto</h3>
          </div>

          {/* Camera Viewfinder */}
          <div style={{
            flex: 1,
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            background: '#010414',
            overflow: 'hidden'
          }}>
            {/* Circle overlay on top of video stream */}
            <div style={{
              width: '280px',
              height: '280px',
              borderRadius: '50%',
              overflow: 'hidden',
              position: 'relative',
              border: '2px dashed rgba(255, 255, 255, 0.8)',
              boxShadow: '0 0 0 9999px rgba(2, 7, 31, 0.6)',
              zIndex: 10,
              pointerEvents: 'none'
            }} />
            
            <video 
              ref={videoRef}
              autoPlay 
              playsInline
              style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                objectFit: 'cover'
              }}
            />
          </div>

          {/* Action Buttons */}
          <div style={{
            width: '100%',
            height: '100px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-around',
            background: 'linear-gradient(180deg, #1e5c78 0%, #03175a 100%)',
            padding: '0 20px',
            borderTop: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <button 
              type="button"
              onClick={() => {
                stopCamera();
                setShowCameraModal(false);
              }}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#e0f2fe',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Cancelar
            </button>
            
            {/* Capture button styled as a shutter */}
            <button 
              type="button"
              onClick={capturePhoto}
              style={{
                width: '68px',
                height: '68px',
                borderRadius: '50%',
                background: '#ffffff',
                border: '4px solid #2790b0',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(39, 144, 176, 0.4)'
              }}
            >
              <div style={{
                width: '46px',
                height: '46px',
                borderRadius: '50%',
                background: '#ffffff',
                border: '2px solid #03175a'
              }} />
            </button>
            
            {/* Space placeholder to balance the layout */}
            <div style={{ width: '60px' }} />
          </div>
        </div>
      )}

      {/* Cropper Modal (Mover y redimensionar) */}
      {cropImage && (
        <div className="dialog-overlay" style={{ background: '#02071f', zIndex: 1200, padding: '0', flexDirection: 'column' }}>
          {/* Header */}
          <div style={{
            width: '100%',
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #03175a 0%, #1e5c78 100%)',
            color: '#ffffff',
            position: 'relative',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: 30
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '700', letterSpacing: '0.5px' }}>Mover y redimensionar</h3>
          </div>

          {/* Viewport / Crop area */}
          <div 
            style={{
              flex: 1,
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              background: '#010414',
              overflow: 'hidden',
              cursor: 'move'
            }}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleMouseUp}
          >
            {/* The full image is visible here in the background */}
            <img 
              ref={imgRef}
              src={cropImage} 
              alt="Crop Preview"
              onLoad={handleImageLoad}
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                width: `${imageDisplaySize.width}px`,
                height: `${imageDisplaySize.height}px`,
                transform: `translate(-50%, -50%) translate(${offset.x}px, ${offset.y}px) scale(${scale})`,
                transformOrigin: 'center center',
                maxWidth: 'none',
                maxHeight: 'none',
                pointerEvents: 'none',
                userSelect: 'none'
              }}
            />

            {/* The clear circular spotlight on top, with a translucent backdrop shadow */}
            <div 
              style={{
                width: '280px',
                height: '280px',
                borderRadius: '50%',
                border: '2px solid rgba(255, 255, 255, 0.85)',
                boxShadow: '0 0 0 9999px rgba(2, 7, 31, 0.65)', // 65% opacity navy-black mask
                pointerEvents: 'none',
                zIndex: 20,
                position: 'absolute'
              }}
            />
          </div>

          {/* Zoom Controls */}
          <div style={{
            width: '100%',
            background: 'linear-gradient(180deg, #1e5c78 0%, #03175a 100%)',
            padding: '24px 20px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px',
            boxShadow: '0 -4px 12px rgba(0,0,0,0.1)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', width: '80%', maxWidth: '300px', gap: '12px' }}>
              <span style={{ color: '#bae6fd', fontSize: '12px', fontWeight: '600' }}>A-</span>
              <input 
                type="range" 
                min="1" 
                max="3" 
                step="0.01" 
                value={scale} 
                onChange={(e) => setScale(parseFloat(e.target.value))}
                style={{
                  flex: 1,
                  accentColor: '#2790b0',
                  height: '6px',
                  borderRadius: '3px',
                  outline: 'none',
                  background: 'rgba(255,255,255,0.2)'
                }}
              />
              <span style={{ color: '#bae6fd', fontSize: '12px', fontWeight: '600' }}>A+</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{
            width: '100%',
            height: '75px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: '#03175a',
            padding: '0 30px',
            borderTop: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <button 
              type="button"
              onClick={() => setCropImage(null)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#e0f2fe',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Cancelar
            </button>
            <button 
              type="button"
              onClick={handleSaveCrop}
              style={{
                background: 'linear-gradient(135deg, #1e5c78 0%, #2790b0 100%)',
                border: 'none',
                color: '#ffffff',
                fontSize: '16px',
                fontWeight: '700',
                padding: '10px 28px',
                borderRadius: '24px',
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(39, 144, 176, 0.3)'
              }}
            >
              Seleccionar
            </button>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
