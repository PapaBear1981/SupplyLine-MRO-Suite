import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { login } from '../../store/authSlice';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';

const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [validated, setValidated] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.auth);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!username || !password) {
      setValidated(true);
      return;
    }

    setValidated(true);

    try {
      await dispatch(login({ username, password })).unwrap();
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {error && (
        <Alert variant="destructive" className="animate-slide-up">
          <AlertDescription>
            {error.message || error.error || 'Login failed. Please try again.'}
          </AlertDescription>
        </Alert>
      )}

      <div className="space-y-2 animate-slide-up" style={{ animationDelay: '0.1s', animationFillMode: 'backwards' }}>
        <Label htmlFor="username" className="text-sm font-medium">
          Employee Number
        </Label>
        <Input
          id="username"
          type="text"
          placeholder="Enter your employee number"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className={`transition-all ${validated && !username ? 'border-destructive focus-visible:ring-destructive' : ''}`}
          required
          autoComplete="username"
        />
        {validated && !username && (
          <p className="text-xs text-destructive animate-slide-up">
            Please provide your employee number.
          </p>
        )}
      </div>

      <div className="space-y-2 animate-slide-up" style={{ animationDelay: '0.2s', animationFillMode: 'backwards' }}>
        <Label htmlFor="password" className="text-sm font-medium">
          Password
        </Label>
        <div className="relative">
          <Input
            id="password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={`pr-10 transition-all ${validated && !password ? 'border-destructive focus-visible:ring-destructive' : ''}`}
            required
            autoComplete="current-password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        {validated && !password && (
          <p className="text-xs text-destructive animate-slide-up">
            Please provide a password.
          </p>
        )}
      </div>

      <div className="flex items-center space-x-2 animate-slide-up" style={{ animationDelay: '0.3s', animationFillMode: 'backwards' }}>
        <input
          id="rememberMe"
          type="checkbox"
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
          className="h-4 w-4 rounded border-input bg-background ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
        />
        <Label
          htmlFor="rememberMe"
          className="text-sm font-normal cursor-pointer select-none"
        >
          Remember me
        </Label>
      </div>

      <Button
        type="submit"
        className="w-full animate-slide-up transition-all hover:scale-[1.02] active:scale-[0.98]"
        style={{ animationDelay: '0.4s', animationFillMode: 'backwards' }}
        disabled={loading}
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Logging in...
          </>
        ) : (
          'Login'
        )}
      </Button>
    </form>
  );
};

export default LoginForm;
