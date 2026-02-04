/**
 * Validation Utils Tests
 */

import { loginSchema, registerSchema, profileSchema } from '../../utils/validation';

describe('Validation Schemas', () => {
  describe('loginSchema', () => {
    it('should validate correct login data', () => {
      const validData = {
        email: 'test@example.com',
        password: 'password123',
      };
      
      const result = loginSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject invalid email', () => {
      const invalidData = {
        email: 'invalid-email',
        password: 'password123',
      };
      
      const result = loginSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].path).toContain('email');
      }
    });

    it('should reject empty password', () => {
      const invalidData = {
        email: 'test@example.com',
        password: '',
      };
      
      const result = loginSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('registerSchema', () => {
    it('should validate correct registration data', () => {
      const validData = {
        email: 'test@example.com',
        password: 'password123',
        confirmPassword: 'password123',
        displayName: 'Test User',
      };
      
      const result = registerSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject password without number', () => {
      const invalidData = {
        email: 'test@example.com',
        password: 'passwordonly',
        confirmPassword: 'passwordonly',
      };
      
      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject mismatched passwords', () => {
      const invalidData = {
        email: 'test@example.com',
        password: 'password123',
        confirmPassword: 'different123',
      };
      
      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].path).toContain('confirmPassword');
      }
    });

    it('should reject short password', () => {
      const invalidData = {
        email: 'test@example.com',
        password: 'pass1',
        confirmPassword: 'pass1',
      };
      
      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('profileSchema', () => {
    it('should validate correct profile data', () => {
      const validData = {
        displayName: 'Test User',
        bio: 'This is my bio',
      };
      
      const result = profileSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should allow empty optional fields', () => {
      const validData = {};
      
      const result = profileSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject too long display name', () => {
      const invalidData = {
        displayName: 'a'.repeat(101),
      };
      
      const result = profileSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject too long bio', () => {
      const invalidData = {
        bio: 'a'.repeat(501),
      };
      
      const result = profileSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });
});