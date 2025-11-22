import UserCheckouts from '../components/checkouts/UserCheckouts';

const UserCheckoutsPageNew = () => {
  return (
    <div className="w-full space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-foreground">My Checkouts</h1>
      <UserCheckouts />
    </div>
  );
};

export default UserCheckoutsPageNew;
