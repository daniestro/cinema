import { getHeroSlides } from '@/features/home/server/heroData';
import { HeroRotator } from '@/features/home/components/HeroRotator';

export async function Hero() {
  const slides = await getHeroSlides();
  return <HeroRotator slides={slides} />;
}
