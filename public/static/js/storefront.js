(function () {
	const grid = document.getElementById("product-grid");
	if (!grid) return;

	const cards = Array.from(grid.querySelectorAll(".catalog-product"));
	const searchInput = document.querySelector('form.search input[name="q"]');
	const resultCount = document.getElementById("catalog-result-count");
	const emptyState = document.getElementById("catalog-empty-state");
	const favoritesFilter = document.getElementById("favorites-filter");
	const favoritesCount = document.getElementById("favorites-count");
	const sortSelect = document.getElementById("catalog-sort");
	const favoriteKey = "everyday-store:favorites";
	const initialParams = new URLSearchParams(window.location.search);
	const serverFiltered = initialParams.has("q") || initialParams.has("category");
	const selectedCategoryButton = document.querySelector("[data-category-filter].is-active");
	let activeCategory = selectedCategoryButton ? selectedCategoryButton.dataset.categoryFilter : "";
	let showFavoritesOnly = false;
	let favorites = new Set();

	try {
		const storedFavorites = JSON.parse(window.localStorage.getItem(favoriteKey) || "[]");
		if (Array.isArray(storedFavorites)) favorites = new Set(storedFavorites);
	} catch {
		favorites = new Set();
	}

	function updateFavoriteButtons() {
		document.querySelectorAll("[data-favorite-id]").forEach(function (button) {
			const isFavorite = favorites.has(button.dataset.favoriteId);
			button.setAttribute("aria-pressed", String(isFavorite));
			button.setAttribute(
				"aria-label",
				(isFavorite ? "Remove " : "Save ") + button.closest(".catalog-product").querySelector(".product-name").textContent.trim() + " " + (isFavorite ? "from" : "to") + " favorites"
			);
			button.innerHTML = '<i class="' + (isFavorite ? "fas" : "far") + ' fa-heart" aria-hidden="true"></i>';
		});
		favoritesCount.textContent = String(favorites.size);
	}

	function sortCards() {
		const sortMode = sortSelect.value;
		const sorted = cards.slice().sort(function (first, second) {
			if (sortMode === "name-asc") {
				return first.dataset.productName.localeCompare(second.dataset.productName);
			}
			if (sortMode === "price-asc") {
				return Number(first.dataset.productPrice) - Number(second.dataset.productPrice);
			}
			if (sortMode === "price-desc") {
				return Number(second.dataset.productPrice) - Number(first.dataset.productPrice);
			}
			return cards.indexOf(first) - cards.indexOf(second);
		});
		sorted.forEach(function (card) { grid.appendChild(card); });
	}

	function renderCatalog() {
		const query = searchInput ? searchInput.value.trim().toLocaleLowerCase() : "";
		let visibleCount = 0;

		cards.forEach(function (card) {
			const matchesQuery = !query
				|| card.dataset.productName.includes(query)
				|| card.dataset.productDescription.includes(query)
				|| card.querySelector(".text-muted").textContent.toLocaleLowerCase().includes(query);
			const matchesCategory = !activeCategory || card.dataset.productCategory === activeCategory;
			const matchesFavorites = !showFavoritesOnly || favorites.has(card.dataset.productId);
			const isVisible = matchesQuery && matchesCategory && matchesFavorites;
			card.hidden = !isVisible;
			if (isVisible) visibleCount += 1;
		});

		resultCount.textContent = visibleCount + (visibleCount === 1 ? " product" : " products");
		emptyState.hidden = visibleCount !== 0;
		sortCards();
	}

	document.querySelectorAll("[data-category-filter]").forEach(function (button) {
		button.addEventListener("click", function () {
			if (serverFiltered) {
				const url = new URL(window.location.href);
				if (button.dataset.categoryFilter) {
					url.searchParams.set("category", button.dataset.categoryFilter);
				} else {
					url.searchParams.delete("category");
				}
				window.location.assign(url);
				return;
			}
			activeCategory = button.dataset.categoryFilter;
			document.querySelectorAll("[data-category-filter]").forEach(function (categoryButton) {
				const isActive = categoryButton === button;
				categoryButton.classList.toggle("is-active", isActive);
				categoryButton.classList.toggle("btn-primary", isActive);
				categoryButton.classList.toggle("btn-outline-secondary", !isActive);
				categoryButton.setAttribute("aria-pressed", String(isActive));
			});
			renderCatalog();
		});
	});

	if (searchInput) searchInput.addEventListener("input", renderCatalog);
	sortSelect.addEventListener("change", renderCatalog);

	if (favoritesFilter) {
		favoritesFilter.addEventListener("click", function () {
			showFavoritesOnly = !showFavoritesOnly;
			favoritesFilter.setAttribute("aria-pressed", String(showFavoritesOnly));
			favoritesFilter.classList.toggle("btn-danger", showFavoritesOnly);
			favoritesFilter.classList.toggle("btn-outline-danger", !showFavoritesOnly);
			renderCatalog();
		});
	}

	document.querySelectorAll("[data-favorite-id]").forEach(function (button) {
		button.addEventListener("click", function () {
			const productId = button.dataset.favoriteId;
			if (favorites.has(productId)) {
				favorites.delete(productId);
			} else {
				favorites.add(productId);
			}
			try {
				window.localStorage.setItem(favoriteKey, JSON.stringify(Array.from(favorites)));
			} catch {
				// Keep favorites available for this page view if browser storage is disabled.
			}
			updateFavoriteButtons();
			renderCatalog();
		});
	});

	const clearSearchButton = document.getElementById("clear-catalog-search");
	if (clearSearchButton) {
		clearSearchButton.addEventListener("click", function () {
			if (serverFiltered) {
				window.location.assign(window.location.pathname);
				return;
			}
			if (searchInput) searchInput.value = "";
			activeCategory = "";
			showFavoritesOnly = false;
			document.querySelectorAll("[data-category-filter]").forEach(function (button, index) {
				const isActive = index === 0;
				button.classList.toggle("is-active", isActive);
				button.classList.toggle("btn-primary", isActive);
				button.classList.toggle("btn-outline-secondary", !isActive);
				button.setAttribute("aria-pressed", String(isActive));
			});
			if (favoritesFilter) {
				favoritesFilter.setAttribute("aria-pressed", "false");
				favoritesFilter.classList.remove("btn-danger");
				favoritesFilter.classList.add("btn-outline-danger");
			}
			renderCatalog();
			if (window.location.search) window.history.replaceState({}, "", window.location.pathname);
		});
	}

	updateFavoriteButtons();
	renderCatalog();
})();
