import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Input, Button, Checkbox, Alert, Space } from 'antd';
import { UserOutlined, LockOutlined, EyeInvisibleOutlined, EyeOutlined } from '@ant-design/icons';
import { login } from '../../store/authSlice';

const LoginForm = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.auth);

  const handleSubmit = async (values) => {
    try {
      await dispatch(login({
        username: values.employeeNumber,
        password: values.password,
      })).unwrap();
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <Form
      form={form}
      name="login"
      onFinish={handleSubmit}
      layout="vertical"
      requiredMark={false}
      size="large"
    >
      {error && (
        <Alert
          message="Authentication Failed"
          description={error.message || error.error || 'Login failed. Please try again.'}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Form.Item
        name="employeeNumber"
        label={<span style={{ fontWeight: 500, color: '#16325c' }}>Employee Number</span>}
        rules={[
          {
            required: true,
            message: 'Please enter your employee number',
          },
        ]}
      >
        <Input
          prefix={<UserOutlined style={{ color: '#8a96a8' }} />}
          placeholder="Enter employee number"
          autoComplete="username"
          style={{
            height: 44,
            borderRadius: 6,
          }}
        />
      </Form.Item>

      <Form.Item
        name="password"
        label={<span style={{ fontWeight: 500, color: '#16325c' }}>Password</span>}
        rules={[
          {
            required: true,
            message: 'Please enter your password',
          },
        ]}
      >
        <Input.Password
          prefix={<LockOutlined style={{ color: '#8a96a8' }} />}
          placeholder="Enter password"
          autoComplete="current-password"
          iconRender={(visible) => (visible ? <EyeOutlined /> : <EyeInvisibleOutlined />)}
          style={{
            height: 44,
            borderRadius: 6,
          }}
        />
      </Form.Item>

      <Form.Item name="remember" valuePropName="checked" style={{ marginBottom: 24 }}>
        <Checkbox>
          <span style={{ color: '#54698d' }}>Remember me</span>
        </Checkbox>
      </Form.Item>

      <Form.Item style={{ marginBottom: 0 }}>
        <Button
          type="primary"
          htmlType="submit"
          loading={loading}
          block
          style={{
            height: 44,
            borderRadius: 6,
            fontWeight: 600,
            fontSize: 14,
            background: '#0070d2',
            boxShadow: '0 4px 12px rgba(0, 112, 210, 0.3)',
          }}
        >
          {loading ? 'Authenticating...' : 'Sign In'}
        </Button>
      </Form.Item>
    </Form>
  );
};

export default LoginForm;
