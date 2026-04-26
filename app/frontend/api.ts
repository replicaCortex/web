import { RegisterDTO, LoginDTO, ForgotPasswordDTO, ResetPasswordDTO } from '../../../app/auth/schemas';
import { UserCreate, UserRead } from '../../../app/users/schemas';

const apiURL = 'http://localhost:8000';

const register = async (data: RegisterDTO) => {
  const response = await fetch(`${apiURL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response.json();
};

const login = async (data: LoginDTO) => {
  const response = await fetch(`${apiURL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response.json();
};

const forgotPassword = async (data: ForgotPasswordDTO) => {
  const response = await fetch(`${apiURL}/auth/forgot-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response.json();
};

const resetPassword = async (data: ResetPasswordDTO) => {
  const response = await fetch(`${apiURL}/auth/reset-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response.json();
};

const createUser = async (data: UserCreate) => {
  const response = await fetch(`${apiURL}/users`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response.json();
};

const getUsers = async () => {
  const response = await fetch(`${apiURL}/users`);
  return response.json();
};

const getUser = async (id: string) => {
  const response = await fetch(`${apiURL}/users/${id}`);
  return response.json();
};

const deleteUser = async (id: string) => {
  const response = await fetch(`${apiURL}/users/${id}`, {
    method: 'DELETE',
  });
  return response.json();
};
import { UserCreate, UserRead } from '../../../app/users/schemas';

interface RegisterDTO {
  username: string;
  email: string;
  password: string;
}

interface LoginDTO {
  email: string;
  password: string;
}

interface ForgotPasswordDTO {
  email: string;
}

interface ResetPasswordDTO {
  token: string;
  new_password: string;
}

interface UserProfileResponse {
  id: string;
  username: string;
  email: string;
  os: string;
  totaltime: number;
  created_at: Date;
  updated_at: Date;
}

interface MessageResponse {
  message: string;
}
