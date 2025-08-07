export const RecipeTable = () => {
  const recipes = [
    {
      title: "🏨 Hotel Search",
      link: "./hotel-search.md",
      appUrl: "https://hotel-search-recipe.superlinked.io/",
      keyFeatures: ["Natural Language Queries", "Multi-modal Semantic Search"],
      modalities: ["Text", "Numbers", "Categories"],
      useCase: {
        title: "Multi-Modal Semantic Search",
        link: "./multi-modal-semantic-search.md"
      }
    },
    {
      title: "🛍️ E-Commerce RecSys",
      link: "./ecomm-recsys.md",
      appUrl: "https://recsys-nlq-demo.superlinked.io/",
      keyFeatures: ["Item-to-item recommendations", "Item-to-user recommendations", "Collaborative filtering"],
      modalities: ["Image", "Text", "Numbers", "Categories"],
      useCase: {
        title: "Recommendation System",
        link: "./recommendation-system.md"
      }
    }
  ];

  return (
    <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-2 not-prose">
      {recipes.map((recipe, index) => (
        <div
          key={index}
          className="group relative overflow-hidden rounded-xl border border-zinc-950/10 dark:border-white/10 bg-white dark:bg-zinc-950 p-6 shadow-sm transition-all duration-200 hover:shadow-lg hover:border-zinc-950/20 dark:hover:border-white/20 flex flex-col"
        >
          {/* Header with title */}
          <div className="mb-3">
            <h3 className="text-lg font-semibold text-zinc-900 dark:text-white">
              {recipe.title}
            </h3>
          </div>

          {/* Use Case - Prominent */}
          <div className="mb-4">
            <div className="inline-flex items-center px-3 py-2 text-sm font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 rounded-lg border border-zinc-200 dark:border-zinc-700">
              {recipe.useCase.title}
            </div>
          </div>

          {/* Key Features */}
          <div className="mb-4">
            <h4 className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
              Key Features
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {recipe.keyFeatures.map((feature, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300 rounded-md"
                >
                  {feature}
                </span>
              ))}
            </div>
          </div>

          {/* Modalities */}
          <div className="mb-6 flex-grow">
            <h4 className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
              Modalities
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {recipe.modalities.map((modality, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300 rounded-md"
                >
                  {modality}
                </span>
              ))}
            </div>
          </div>

          {/* CTAs */}
          <div className="flex items-center justify-between pt-4 border-t border-zinc-950/10 dark:border-white/10">
            <a
              href={recipe.link}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-white rounded-md transition-all duration-200 hover:brightness-110"
              style={{ backgroundColor: '#FF5722' }}
            >
              Read more
            </a>
            <a
              href={recipe.appUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-zinc-600 dark:text-zinc-400 transition-colors"
              style={{ color: '#FF5722' }}
            >
              Live app →
            </a>
          </div>
        </div>
      ))}
    </div>
  );
}; 