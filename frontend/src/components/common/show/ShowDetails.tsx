import type { Show } from '#/lib/interfaces/shows'

interface ShowDetailsProps {
  show: Show
}

export function ShowDetails({ show }: ShowDetailsProps) {
  return (
    <div className="flex flex-col text-base sm:text-lg lg:text-2xl">
      <div>
        <p className="mt-6 sm:mt-8 mb-3 sm:mb-4 text-xl sm:text-2xl md:text-3xl text-primary">About the show:</p>
        <p>{show.description}</p>
      </div>
      <div className="mt-6 sm:mt-8 flex flex-wrap justify-center gap-8 sm:gap-12">
        <img
          src={show.cardImage}
          alt={show.title}
          className="w-full max-w-sm object-cover"
        />
        <div className="flex flex-col lg:mt-12">
          <p className="mt-3 sm:mt-4 mb-3 sm:mb-4 text-xl sm:text-2xl md:text-3xl text-primary">Cast:</p>
          <p>{show.cast}</p>
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
  )
}
