import { getRails } from '@/features/home/server/rails';
import { NumberedRail } from '@/features/home/components/NumberedRail';

export async function HomeRails() {
  const rails = await getRails();
  return (
    <div className="space-y-section py-section">
      {rails.map((rail) => (
        <NumberedRail key={rail.genre} rail={rail} />
      ))}
    </div>
  );
}
