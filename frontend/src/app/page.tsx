import { Hero } from '@/features/home/components/Hero';
import { HomeRails } from '@/features/home/components/HomeRails';
import { InfoBlock } from '@/features/home/components/InfoBlock';

export default function HomePage() {
  return (
    <>
      <Hero />
      <InfoBlock />
      <HomeRails />
    </>
  );
}
