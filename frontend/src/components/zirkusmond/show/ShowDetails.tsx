import type { Show } from '#/interfaces/show'
import SectionCard from '../general/SectionCard'
import { SERVER_API_URL } from '#/lib/api.ts'

interface ShowDetailsProps {
  show: Show
}

export function ShowDetails({ show }: ShowDetailsProps) {
  return (
    <SectionCard>
      <div className="flex flex-col text-base sm:text-lg lg:text-2xl">
        <div>
          <h3 className="mt-6 sm:mt-8 mb-3 sm:mb-4">About the show:</h3>
          <div dangerouslySetInnerHTML={{ __html: show.description }} />
        </div>
        <div className="mt-6 sm:mt-8 flex flex-wrap justify-center gap-8 sm:gap-12">
          <img
            src={`${SERVER_API_URL}${show.cardImage}`}
            alt={show.title}
            className="w-full max-w-sm object-cover"
          />
          <div className="flex flex-col lg:mt-12">
            <h3 className="mt-3 sm:mt-4 mb-3 sm:mb-4">Cast:</h3>
            <div dangerouslySetInnerHTML={{ __html: show.cast }} />
          </div>
        </div>
        <div className="mt-6 sm:mt-8 flex flex-wrap items-center justify-evenly gap-4">
          {show.videoLink && (
            <a
              className="text-center text-lg sm:text-xl md:text-2xl underline hover:text-white"
              href={show.videoLink}
              target="_blank"
              rel="noreferrer"
            >
              Trailer
            </a>
          )}
          {show.websiteLink && (
            <a
              className="text-center text-lg sm:text-xl md:text-2xl underline hover:text-white"
              href={show.websiteLink}
              target="_blank"
              rel="noreferrer"
            >
              Company's website
            </a>
          )}
        </div>
      </div>
    </SectionCard>
  )
}
