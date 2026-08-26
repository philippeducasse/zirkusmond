import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '#/components/ui/carousel.tsx'
import SectionDivider from '#/components/zirkusmond/general/SectionDivider'
import ContentSection from '../general/ContentSection'
import * as m from '#/paraglide/messages'

const GALLERY_IMAGES = Array.from(
  { length: 10 },
  (_, i) => `/images/gallery/img-${i}.webp`,
)

export default function GallerySection() {
  return (
    <ContentSection>
      {/* TODO: prepend a video slide once media/video/video.mp4 exists */}
      <Carousel className="mx-auto max-w-4xl">
        <CarouselContent>
          {GALLERY_IMAGES.map((src, i) => (
            <CarouselItem key={src}>
              <img
                src={src}
                alt={m.gallery_image({ number: i + 1 })}
                className="aspect-video w-full object-cover"
              />
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
      <SectionDivider type="flower" />
    </ContentSection>
  )
}
