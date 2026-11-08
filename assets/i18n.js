/**
 * aviisrgames.com - Declarative Multilingual i18n Engine (assets/i18n.js)
 *
 * ============================================================================
 * HOW TO REPLACE, EDIT, OR ADD A LANGUAGE IN 1 STEP:
 * ============================================================================
 * 1. Global language metadata lives in `window.AVIISR_LANGS` below (code -> { nativeName, englishName, dir }).
 *    To replace a language code (e.g., swapping `nb` for `pl`), change its entry in `AVIISR_LANGS` and update
 *    its key in `AVIISR_STRINGS` (or in the page's local `translations` dictionary).
 * 2. Every game page calls `AviisrI18n.init({ supported: [...], translations: {...}, defaultLang: 'en' })`.
 *    - `supported` controls which languages appear in the page's `<select id="lang-switcher">` dropdown.
 *    - Built-in 19-language studio & game dictionaries in `AVIISR_STRINGS` provide automatic translations for
 *      shared UI, game descriptions, playables, and support headings, while page-level `translations` override
 *      any page-specific keys.
 *
 * Security & Anti-XSS:
 * - Strictly uses `textContent` and `replaceChildren()` (zero `innerHTML` or `outerHTML`).
 * - Strictly validates `?lang=` and `#hash` against the page's `supported` whitelist.
 */

(function () {
  'use strict';

  var AVIISR_LANGS = {
    'en': { nativeName: 'English', englishName: 'English', dir: 'ltr' },
    'he': { nativeName: 'עברית', englishName: 'Hebrew', dir: 'rtl' },
    'ar': { nativeName: 'العربية', englishName: 'Arabic', dir: 'rtl' },
    'es': { nativeName: 'Español', englishName: 'Spanish', dir: 'ltr' },
    'fr': { nativeName: 'Français', englishName: 'French', dir: 'ltr' },
    'de': { nativeName: 'Deutsch', englishName: 'German', dir: 'ltr' },
    'it': { nativeName: 'Italiano', englishName: 'Italian', dir: 'ltr' },
    'nl': { nativeName: 'Nederlands', englishName: 'Dutch', dir: 'ltr' },
    'pt-BR': { nativeName: 'Português (Brasil)', englishName: 'Portuguese (Brazil)', dir: 'ltr' },
    'tr': { nativeName: 'Türkçe', englishName: 'Turkish', dir: 'ltr' },
    'ru': { nativeName: 'Русский', englishName: 'Russian', dir: 'ltr' },
    'ja': { nativeName: '日本語', englishName: 'Japanese', dir: 'ltr' },
    'ko': { nativeName: '한국어', englishName: 'Korean', dir: 'ltr' },
    'zh-TW': { nativeName: '繁體中文', englishName: 'Chinese (Traditional)', dir: 'ltr' },
    'zh-CN': { nativeName: '简体中文', englishName: 'Chinese (Simplified)', dir: 'ltr' },
    'sv': { nativeName: 'Svenska', englishName: 'Swedish', dir: 'ltr' },
    'da': { nativeName: 'Dansk', englishName: 'Danish', dir: 'ltr' },
    'nb': { nativeName: 'Norsk', englishName: 'Norwegian', dir: 'ltr' },
    'fi': { nativeName: 'Suomi', englishName: 'Finnish', dir: 'ltr' }
  };

  var AVIISR_STRINGS = {
    'en': {
      heroTitle: 'aviisr-games',
      heroSub: 'Independent mobile games studio. Strategy, puzzles, and arcade games crafted for iOS and Android.',
      playablesTitle: '🎮 Play In Your Browser',
      playablesSub: 'Experience quick playable web teasers and trainers without installing an app:',
      p1Desc: "Solve today's puzzle with smart logic hints.",
      p2Desc: 'Navigate 3 months as Prime Minister.',
      p3Desc: 'Master basic casino odds and streak counts.',
      playNow: 'Play Now',
      gamesTitle: 'Our Games',
      hubLink: 'Game Hub',
      ninelyDesc: 'Minimalist number puzzle with smart hints that teach logic step-by-step. 18 languages, daily challenges & duels.',
      me2030Desc: "Deep political strategy simulation set in 2030. Choose from 8 regional capitals and read tomorrow's morning front page.",
      mprDesc: 'Fast-paced 60 FPS arcade bicycle newspaper courier. Dodge barking dogs and traffic across 7 expanding neighborhoods.',
      baylightDesc: 'A calm, satisfying one-thumb depot sorting puzzle. Stack three matching crates and ship your cargo trucks.',
      casinoDesc: 'Blackjack with built-in strategy coach, Texas Hold’em against computer players, and European/American Roulette (strictly virtual chips).',
      milaDesc: 'English learning for Hebrew-speaking children (grades 1–6). 100% offline, zero ads, no subscriptions, fully COPPA compliant.',
      contactTitle: 'Studio Contact & Support',
      contactSub: 'Player inquiries, bug reports, ad privacy requests, or business correspondence:',
      navAllGames: 'All Games',
      navPrivacy: 'Privacy Policy',
      navSupport: 'Support',
      smartHint: 'Smart Hint',
      restart: '↺ Restart',
      openApp: 'Open in App',
      won: 'Board Cleared!',
      statCoalition: 'Coalition',
      statEconomy: 'Economy',
      statStability: 'Stability',
      streak: 'Streak',
      accuracy: 'Accuracy',
      hands: 'Hands',
      dealerUpcard: 'Dealer Upcard',
      yourHand: 'Your Hand',
      actHit: 'HIT',
      actStand: 'STAND',
      actDouble: 'DOUBLE',
      actSplit: 'SPLIT'
    },
    'he': {
      heroTitle: 'aviisr-games',
      heroSub: 'סטודיו עצמאי למשחקי מובייל. אסטרטגיה, פאזלים וארקייד ל-iOS ו-Android.',
      playablesTitle: '🎮 לשחק עכשיו בדפדפן',
      playablesSub: 'התנסו במשחקים קצרים ומאמנים ישירות בדפדפן, ללא צורך בהתקנה:',
      p1Desc: 'פתרו את הלוח היומי עם רמזים חכמים שמסבירים כל צעד.',
      p2Desc: 'נהלו 3 חודשים כראש ממשלה והדפיסו את העיתון.',
      p3Desc: "תרגלו אסטרטגיה בסיסית וסיכויי בלאק ג'ק.",
      playNow: 'לשחק עכשיו',
      gamesTitle: 'המשחקים שלנו',
      hubLink: 'עמוד המשחק',
      ninelyDesc: 'פאזל מספרים מינימליסטי עם רמזים חכמים. 18 שפות, אתגרים יומיים ודו-קרב חברים.',
      me2030Desc: 'סימולציית אסטרטגיה פוליטית לשנת 2030. 8 ערי בירה, קבלת החלטות וקריאת שער העיתון של מחר.',
      mprDesc: 'משחק ארקייד מהיר של שליח עיתונים על אופניים ב-60 FPS. התחמקו מכלבים ומכוניות ב-7 שכונות שונות.',
      baylightDesc: 'פאזל מיון רגוע ומהנה באגודל אחת. סדרו שלשות ארגזים זהים ושלחו את המשאיות ליעדן.',
      casinoDesc: "בלאק ג'ק עם מאמן אסטרטגיה מובנה, טקסס הולדם מול המחשב, ורולטה אירופאית ואמריקאית (צ'יפים וירטואליים בלבד).",
      milaDesc: "לימוד ותרגול אנגלית לילדים בכיתות א'-ו'. עובד מלא ללא אינטרנט, ללא פרסומות וללא מנוי.",
      contactTitle: 'יצירת קשר ותמיכה',
      contactSub: 'פניות שחקנים, דיווח על תקלות, בקשות פרטיות או פניות עסקיות:',
      navAllGames: 'כל המשחקים',
      navPrivacy: 'מדיניות פרטיות',
      navSupport: 'תמיכה',
      smartHint: 'רמז חכם',
      restart: '↺ התחלה מחדש',
      openApp: 'פתיחה באפליקציה',
      won: 'הלוח הושלם בהצלחה!',
      statCoalition: 'קואליציה',
      statEconomy: 'כלכלה',
      statStability: 'יציבות',
      streak: 'רצף',
      accuracy: 'דיוק',
      hands: 'ידיים',
      dealerUpcard: 'קלף דילר',
      yourHand: 'היד שלך',
      actHit: 'עוד קלף (Hit)',
      actStand: 'עמוד (Stand)',
      actDouble: 'הכפלה (Double)',
      actSplit: 'פיצול (Split)'
    },
    'ar': {
      heroTitle: 'aviisr-games',
      heroSub: 'استوديو مستقل لألعاب الهواتف المحمولة. ألعاب استراتيجية، ألغاز وأركيد لنظامي iOS و Android.',
      playablesTitle: '🎮 العب الآن في المتصفح',
      playablesSub: 'جرّب ألعاباً مصغرة ومدرّبات تفاعلية مباشرة في متصفحك دون الحاجة لتثبيت تطبيق:',
      p1Desc: 'حل لغز اليوم مع تلميحات منطقية ذكية.',
      p2Desc: 'قُد الحكومة لمدة 3 أشهر واطبع الصفحة الأولى.',
      p3Desc: 'أتقن استراتيجية البلاك جاك والاحتمالات الرياضية.',
      playNow: 'العب الآن',
      gamesTitle: 'ألعابنا',
      hubLink: 'صفحة اللعبة',
      ninelyDesc: 'لغز أرقام أنيق مع تلميحات ذكية تشرح كل خطوة. 18 لغة وتحديات يومية.',
      me2030Desc: 'محاكاة استراتيجية سياسية عميقة لعام 2030. اختر من بين 8 عواصم إقليمية واقرأ صحيفة الغد.',
      mprDesc: 'لعبة أركيد سريعة لتوصيل الصحف بالدراجة الهوائية. تجنب الكلاب والسيارات عبر 7 أحياء.',
      baylightDesc: 'لغز فرز هادئ وممتع بإبهام واحد. رتّب 3 صناديق متطابقة وأرسل شاحنات الشحن.',
      casinoDesc: 'بلاك جاك مع مدرّب استراتيجية، تكساس هولدم ضد الكمبيوتر، وروليت أوروبية وأمريكية (رقاقات افتراضية فقط).',
      milaDesc: 'تعليم الإنجليزية للأطفال. يعمل دون اتصال بالإنترنت، بلا إعلانات وبلا اشتراكات.',
      contactTitle: 'التواصل والدعم',
      contactSub: 'استفسارات اللاعبين، تقارير الأخطاء، أو المراسلات الرسمية:',
      navAllGames: 'جميع الألعاب',
      navPrivacy: 'سياسة الخصوصية',
      navSupport: 'الدعم',
      smartHint: 'تلميح ذكي',
      restart: '↺ إعادة البدء',
      openApp: 'فتح في التطبيق',
      won: 'تم حل اللوح بنجاح!',
      statCoalition: 'الائتلاف',
      statEconomy: 'الاقتصاد',
      statStability: 'الاستقرار',
      streak: 'سلسلة',
      accuracy: 'الدقة',
      hands: 'الأيدي',
      dealerUpcard: 'ورقة الموزع',
      yourHand: 'يدك',
      actHit: 'سحب (Hit)',
      actStand: 'وقوف (Stand)',
      actDouble: 'مضاعفة (Double)',
      actSplit: 'تقسيم (Split)'
    },
    'es': {
      heroTitle: 'aviisr-games',
      heroSub: 'Estudio independiente de juegos móviles. Estrategia, puzles y arcade para iOS y Android.',
      playablesTitle: '🎮 Juega en tu navegador',
      playablesSub: 'Prueba avances interactivos y entrenadores directamente en la web sin instalar nada:',
      p1Desc: 'Resuelve el sudoku diario con pistas lógicas paso a paso.',
      p2Desc: 'Gobierna durante 3 meses como Primer Ministro.',
      p3Desc: 'Domina la estrategia básica de Blackjack.',
      playNow: 'Jugar ahora',
      gamesTitle: 'Nuestros Juegos',
      hubLink: 'Página del juego',
      ninelyDesc: 'Puzle numérico minimalista con pistas inteligentes paso a paso. 18 idiomas, retos diarios y duelos.',
      me2030Desc: 'Simulación de estrategia política en 2030. Elige entre 8 capitales y lee la portada de mañana.',
      mprDesc: 'Arcade de reparto de periódicos en bicicleta a 60 FPS por 7 vecindarios.',
      baylightDesc: 'Puzle relajante de clasificación en almacén con un solo pulgar.',
      casinoDesc: 'Blackjack con entrenador de estrategia, Texas Hold’em y Ruleta (solo fichas virtuales).',
      milaDesc: 'Aprendizaje de inglés para niños (100% sin conexión, sin anuncios ni suscripciones).',
      contactTitle: 'Contacto y Soporte',
      contactSub: 'Consultas de jugadores, reportes de errores o contacto comercial:',
      navAllGames: 'Todos los juegos',
      navPrivacy: 'Privacidad',
      navSupport: 'Soporte',
      smartHint: 'Pista inteligente',
      restart: '↺ Reiniciar',
      openApp: 'Abrir en la app',
      won: '¡Tablero completado!',
      statCoalition: 'Coalición',
      statEconomy: 'Economía',
      statStability: 'Estabilidad',
      streak: 'Racha',
      accuracy: 'Precisión',
      hands: 'Manos',
      dealerUpcard: 'Carta del crupier',
      yourHand: 'Tu mano',
      actHit: 'PEDIR',
      actStand: 'PLANTARSE',
      actDouble: 'DOBLAR',
      actSplit: 'DIVIDIR'
    },
    'fr': {
      heroTitle: 'aviisr-games',
      heroSub: 'Studio indépendant de jeux mobiles. Stratégie, puzzles et arcade sur iOS et Android.',
      playablesTitle: '🎮 Jouez dans votre navigateur',
      playablesSub: 'Découvrez nos mini-jeux et entraîneurs interactifs sans installation :',
      p1Desc: 'Résolvez le puzzle du jour avec des indices logiques.',
      p2Desc: 'Dirigez le gouvernement pendant 3 mois de crise.',
      p3Desc: 'Maîtrisez la stratégie de base au Blackjack.',
      playNow: 'Jouer',
      gamesTitle: 'Nos Jeux',
      hubLink: 'Page du jeu',
      ninelyDesc: 'Puzzle numérique minimaliste avec indices intelligents étape par étape en 18 langues.',
      me2030Desc: 'Simulation politique en 2030. Gouvernez l’une des 8 capitales et lisez la une du lendemain.',
      mprDesc: 'Jeu d’arcade de livraison de journaux à vélo à 60 FPS dans 7 quartiers.',
      baylightDesc: 'Puzzle apaisant de tri d’entrepôt à une main.',
      casinoDesc: 'Blackjack avec coach stratégique, Texas Hold’em et Roulette (jetons virtuels uniquement).',
      milaDesc: 'Apprentissage de l’anglais pour enfants (100% hors ligne, sans publicité ni abonnement).',
      contactTitle: 'Contact et Assistance',
      contactSub: 'Questions des joueurs, signalements de bugs ou demandes professionnelles :',
      navAllGames: 'Tous les jeux',
      navPrivacy: 'Confidentialité',
      navSupport: 'Assistance',
      smartHint: 'Indice intelligent',
      restart: '↺ Recommencer',
      openApp: 'Ouvrir dans l’application',
      won: 'Grille résolue !',
      statCoalition: 'Coalition',
      statEconomy: 'Économie',
      statStability: 'Stabilité',
      streak: 'Série',
      accuracy: 'Précision',
      hands: 'Mains',
      dealerUpcard: 'Carte du croupier',
      yourHand: 'Votre main',
      actHit: 'TIRER',
      actStand: 'RESTER',
      actDouble: 'DOUBLER',
      actSplit: 'SÉPARER'
    },
    'de': {
      heroTitle: 'aviisr-games',
      heroSub: 'Unabhängiges Mobile-Games-Studio. Strategie-, Puzzle- und Arcade-Spiele für iOS und Android.',
      playablesTitle: '🎮 Direkt im Browser spielen',
      playablesSub: 'Teste unsere interaktiven Web-Demos und Trainer ohne App-Installation:',
      p1Desc: 'Löse das tägliche Rätsel mit logischen Smart-Hinweisen.',
      p2Desc: 'Regiere 3 Monate lang als Premierminister.',
      p3Desc: 'Trainiere die mathematische Blackjack-Basisstrategie.',
      playNow: 'Jetzt spielen',
      gamesTitle: 'Unsere Spiele',
      hubLink: 'Spielseite',
      ninelyDesc: 'Minimalistisches Zahlenrätsel mit Schritt-für-Schritt-Logikhinweisen in 18 Sprachen.',
      me2030Desc: 'Politische Strategiesimulation im Jahr 2030. Wähle aus 8 Hauptstädten und lies die Schlagzeile von morgen.',
      mprDesc: 'Schnelles 60-FPS-Fahrrad-Zeitungsboten-Arcadespiel durch 7 Nachbarschaften.',
      baylightDesc: 'Entspannendes Ein-Daumen-Lagersortierpuzzle.',
      casinoDesc: 'Blackjack mit Strategie-Trainer, Texas Hold’em und Roulette (rein virtuelle Chips).',
      milaDesc: 'Englischlernen für Kinder (100% offline, werbefrei, kein Abo).',
      contactTitle: 'Kontakt & Support',
      contactSub: 'Spieleranfragen, Fehlermeldungen oder geschäftliche Korrespondenz:',
      navAllGames: 'Alle Spiele',
      navPrivacy: 'Datenschutz',
      navSupport: 'Support',
      smartHint: 'Smart-Hinweis',
      restart: '↺ Neustart',
      openApp: 'In der App öffnen',
      won: 'Gelöst!',
      statCoalition: 'Koalition',
      statEconomy: 'Wirtschaft',
      statStability: 'Stabilität',
      streak: 'Serie',
      accuracy: 'Genauigkeit',
      hands: 'Hände',
      dealerUpcard: 'Dealer-Karte',
      yourHand: 'Deine Hand',
      actHit: 'KARTE (Hit)',
      actStand: 'HALTEN (Stand)',
      actDouble: 'VERDOPPELN',
      actSplit: 'TEILEN'
    },
    'it': {
      heroTitle: 'aviisr-games',
      heroSub: 'Studio indipendente di giochi mobile. Strategia, puzzle e arcade per iOS e Android.',
      playablesTitle: '🎮 Gioca nel browser',
      playablesSub: 'Prova le demo interattive senza installare alcuna app:',
      p1Desc: 'Risolvi il puzzle del giorno con suggerimenti logici.',
      p2Desc: 'Governa per 3 mesi come Primo Ministro.',
      p3Desc: 'Impara la strategia base del Blackjack.',
      playNow: 'Gioca ora',
      gamesTitle: 'I Nostri Giochi',
      hubLink: 'Pagina del gioco',
      ninelyDesc: 'Puzzle numerico minimalista con suggerimenti intelligenti in 18 lingue.',
      me2030Desc: 'Simulazione di strategia politica nel 2030. Scegli tra 8 capitali e leggi la prima pagina di domani.',
      mprDesc: 'Arcade di consegna giornali in bicicletta a 60 FPS in 7 quartieri.',
      baylightDesc: 'Rilassante puzzle di smistamento casse con un solo pollice.',
      casinoDesc: 'Blackjack con allenatore, Texas Hold’em e Roulette (solo fiches virtuali).',
      milaDesc: 'Inglese per bambini (100% offline, zero pubblicità, nessun abbonamento).',
      contactTitle: 'Contatti e Supporto',
      contactSub: 'Domande dei giocatori, segnalazioni di bug o richieste commerciali:',
      navAllGames: 'Tutti i giochi',
      navPrivacy: 'Privacy',
      navSupport: 'Supporto',
      smartHint: 'Suggerimento',
      restart: '↺ Riavvia',
      openApp: 'Apri nell’app',
      won: 'Completato!',
      statCoalition: 'Coalizione',
      statEconomy: 'Economia',
      statStability: 'Stabilità'
    },
    'nl': {
      heroTitle: 'aviisr-games',
      heroSub: 'Onafhankelijke mobiele gamestudio. Strategie-, puzzel- en arcadegames voor iOS en Android.',
      playablesTitle: '🎮 Speel in je browser',
      playablesSub: 'Probeer interactieve webdemo’s zonder een app te installeren:',
      p1Desc: 'Los de dagelijkse puzzel op met slimme logische hints.',
      p2Desc: 'Regeer 3 maanden als premier.',
      p3Desc: 'Oefen de basisstrategie voor Blackjack.',
      playNow: 'Nu spelen',
      gamesTitle: 'Onze Games',
      hubLink: 'Gamepagina',
      ninelyDesc: 'Minimalistische cijferpuzzel met slimme stap-voor-stap hints in 18 talen.',
      me2030Desc: 'Politieke strategiesimulatie in 2030. Kies uit 8 hoofdsteden en lees de voorpagina van morgen.',
      mprDesc: 'Snelle 60 FPS krantenbezorger-arcadegame door 7 wijken.',
      baylightDesc: 'Rustgevende sorteerpuzzel met één duim.',
      casinoDesc: 'Blackjack met strategietrainer, Texas Hold’em en Roulette (alleen virtuele fiches).',
      milaDesc: 'Engels leren voor kinderen (100% offline, geen advertenties, geen abonnement).',
      contactTitle: 'Contact & Ondersteuning',
      contactSub: 'Spelersvragen, bugmeldingen of zakelijke correspondentie:',
      navAllGames: 'Alle games',
      navPrivacy: 'Privacybeleid',
      navSupport: 'Ondersteuning',
      smartHint: 'Slimme hint',
      restart: '↺ Opnieuw',
      openApp: 'Openen in app',
      won: 'Voltooid!',
      statCoalition: 'Coalitie',
      statEconomy: 'Economie',
      statStability: 'Stabiliteit'
    },
    'pt-BR': {
      heroTitle: 'aviisr-games',
      heroSub: 'Estúdio independente de jogos mobile. Estratégia, quebra-cabeças e arcade para iOS e Android.',
      playablesTitle: '🎮 Jogue no Navegador',
      playablesSub: 'Experimente prévias interativas e treinadores sem instalar nenhum aplicativo:',
      p1Desc: 'Resolva o desafio diário com dicas lógicas passo a passo.',
      p2Desc: 'Governe por 3 meses como Primeiro-Ministro.',
      p3Desc: 'Domine a estratégia básica do Blackjack.',
      playNow: 'Jogar agora',
      gamesTitle: 'Nossos Jogos',
      hubLink: 'Página do Jogo',
      ninelyDesc: 'Quebra-cabeça numérico minimalista com dicas inteligentes em 18 idiomas.',
      me2030Desc: 'Simulação de estratégia política em 2030. Escolha entre 8 capitais e leia a manchete de amanhã.',
      mprDesc: 'Arcade de entrega de jornais de bicicleta a 60 FPS por 7 bairros.',
      baylightDesc: 'Quebra-cabeça relaxante de organização de caixas com um polegar.',
      casinoDesc: 'Blackjack com treinador de estratégia, Texas Hold’em e Roleta (apenas fichas virtuais).',
      milaDesc: 'Inglês para crianças (100% offline, sem anúncios e sem assinatura).',
      contactTitle: 'Contato e Suporte',
      contactSub: 'Dúvidas de jogadores, relatos de bugs ou contato comercial:',
      navAllGames: 'Todos os jogos',
      navPrivacy: 'Privacidade',
      navSupport: 'Suporte',
      smartHint: 'Dica Inteligente',
      restart: '↺ Reiniciar',
      openApp: 'Abrir no App',
      won: 'Tabuleiro concluído!',
      statCoalition: 'Coalizão',
      statEconomy: 'Economia',
      statStability: 'Estabilidade'
    },
    'tr': {
      heroTitle: 'aviisr-games',
      heroSub: 'Bağımsız mobil oyun stüdyosu. iOS ve Android için strateji, bulmaca ve arcade oyunları.',
      playablesTitle: '🎮 Tarayıcıda Oyna',
      playablesSub: 'Uygulama indirmeden etkileşimli web demolarını ve eğiticileri deneyin:',
      p1Desc: 'Akıllı mantık ipuçlarıyla günün bulmacasını çözün.',
      p2Desc: 'Başbakan olarak 3 kriz ayını yönetin.',
      p3Desc: 'Temel Blackjack stratejisini ve olasılıkları öğrenin.',
      playNow: 'Şimdi Oyna',
      gamesTitle: 'Oyunlarımız',
      hubLink: 'Oyun Sayfası',
      ninelyDesc: 'Her adımı açıklayan akıllı ipuçlarına sahip minimalist sayı bulmacası. 18 dil desteği.',
      me2030Desc: '2030 yılında geçen derin politik strateji simülasyonu. 8 başkentten birini seçin ve yarının manşetini okuyun.',
      mprDesc: '7 mahallede 60 FPS bisikletli gazete dağıtım arcade oyunu.',
      baylightDesc: 'Tek parmakla oynanan sakinleştirici depo sıralama bulmacası.',
      casinoDesc: 'Strateji koçlu Blackjack, Texas Hold’em ve Rulet (yalnızca sanal çipler).',
      milaDesc: 'Çocuklar için İngilizce öğrenimi (%100 çevrimdışı, reklamsız, aboneliksiz).',
      contactTitle: 'İletişim ve Destek',
      contactSub: 'Oyuncu soruları, hata bildirimleri veya iş yazışmaları:',
      navAllGames: 'Tüm Oyunlar',
      navPrivacy: 'Gizlilik',
      navSupport: 'Destek',
      smartHint: 'Akıllı İpucu',
      restart: '↺ Yeniden Başlat',
      openApp: 'Uygulamada Aç',
      won: 'Tamamlandı!',
      statCoalition: 'Koalisyon',
      statEconomy: 'Ekonomi',
      statStability: 'İstikrar',
      streak: 'Seri',
      accuracy: 'Doğruluk',
      hands: 'El',
      dealerUpcard: 'Krupiye Kartı',
      yourHand: 'Eliniz',
      actHit: 'KART ÇEK',
      actStand: 'DUR',
      actDouble: 'İKİYE KATLA',
      actSplit: 'BÖL'
    },
    'ru': {
      heroTitle: 'aviisr-games',
      heroSub: 'Независимая студия мобильных игр. Стратегии, головоломки и аркады для iOS и Android.',
      playablesTitle: '🎮 Играть в браузере',
      playablesSub: 'Попробуйте интерактивные мини-игры и тренажеры прямо на сайте без установки:',
      p1Desc: 'Решите ежедневную головоломку с умными логическими подсказками.',
      p2Desc: 'Управляйте страной 3 месяца в роли премьер-министра.',
      p3Desc: 'Освойте базовую математическую стратегию блэкджека.',
      playNow: 'Играть',
      gamesTitle: 'Наши игры',
      hubLink: 'Страница игры',
      ninelyDesc: 'Минималистичная числовая головоломка с пошаговыми подсказками на 18 языках.',
      me2030Desc: 'Политический симулятор 2030 года. Выберите одну из 8 столиц и прочитайте утреннюю газету.',
      mprDesc: 'Динамичная аркада (60 FPS) о велокурьере, доставляющем утренние газеты по 7 районам.',
      baylightDesc: 'Спокойная головоломка о сортировке ящиков на складе одним пальцем.',
      casinoDesc: 'Блэкджек с тренером стратегии, Техасский Холдем и Рулетка (только виртуальные фишки).',
      milaDesc: 'Английский для детей (100% офлайн, без рекламы и подписок).',
      contactTitle: 'Контакты и поддержка',
      contactSub: 'Вопросы игроков, сообщения об ошибках и деловые запросы:',
      navAllGames: 'Все игры',
      navPrivacy: 'Конфиденциальность',
      navSupport: 'Поддержка',
      smartHint: 'Умная подсказка',
      restart: '↺ Заново',
      openApp: 'Открыть в приложении',
      won: 'Решено!',
      statCoalition: 'Коалиция',
      statEconomy: 'Экономика',
      statStability: 'Стабильность'
    },
    'ja': {
      heroTitle: 'aviisr-games',
      heroSub: 'インディーモバイルゲームスタジオ。iOS・Android向けの戦略、パズル、アーケードゲーム。',
      playablesTitle: '🎮 ブラウザで今すぐプレイ',
      playablesSub: 'アプリをインストールせずに、ブラウザ上で体験版やトレーナーをプレイできます：',
      p1Desc: '論理的なスマートヒントで今日のパズルを解こう。',
      p2Desc: '首相として3ヶ月間の危機を乗り越えよう。',
      p3Desc: 'ブラックジャックの基本戦略をマスターしよう。',
      playNow: '今すぐプレイ',
      gamesTitle: 'ゲーム一覧',
      hubLink: 'ゲーム詳細',
      ninelyDesc: 'ステップごとに論理を教えるスマートヒント付き数字パズル。18言語対応、デイリー挑戦＆対戦。',
      me2030Desc: '2030年を舞台にした本格政治戦略シミュレーション。8つの首都から選び、明日の朝刊の一面を読もう。',
      mprDesc: '60 FPSの爽快自転車新聞配達アーケード。7つの街で障害物をかわして配達しよう。',
      baylightDesc: '片手で遊べる心地よい倉庫仕分けパズル。同じ木箱を3つ揃えてトラックを出荷しよう。',
      casinoDesc: '戦略コーチ付きブラックジャック、テキサスホールデム、ルーレット（完全仮想チップのみ）。',
      milaDesc: '子ども向け英語学習アプリ（完全オフライン、広告なし、サブスクなし）。',
      contactTitle: 'お問い合わせ・サポート',
      contactSub: 'プレイヤーのお問い合わせ、バグ報告、ビジネス連絡先：',
      navAllGames: 'すべてのゲーム',
      navPrivacy: 'プライバシーポリシー',
      navSupport: 'サポート',
      smartHint: 'スマートヒント',
      restart: '↺ リスタート',
      openApp: 'アプリで開く',
      won: 'クリア！',
      statCoalition: '連立支持',
      statEconomy: '経済',
      statStability: '安定度',
      streak: '連勝',
      accuracy: '正解率',
      hands: 'ハンド数',
      dealerUpcard: 'ディーラーのカード',
      yourHand: 'あなたの手札',
      actHit: 'ヒット (Hit)',
      actStand: 'スタンド (Stand)',
      actDouble: 'ダブル (Double)',
      actSplit: 'スプリット (Split)'
    },
    'ko': {
      heroTitle: 'aviisr-games',
      heroSub: '인디 모바일 게임 스튜디오. iOS 및 Android용 전략, 퍼즐, 아케이드 게임.',
      playablesTitle: '🎮 브라우저에서 바로 플레이',
      playablesSub: '앱 설치 없이 웹에서 미니 게임과 트레이너를 체험해 보세요:',
      p1Desc: '단계별 논리 힌트로 오늘의 퍼즐을 풀어보세요.',
      p2Desc: '총리가 되어 3개월간의 위기를 극복하세요.',
      p3Desc: '블랙잭 기본 전략과 확률을 마스터하세요.',
      playNow: '지금 플레이',
      gamesTitle: '출시 게임',
      hubLink: '게임 허브',
      ninelyDesc: '단계별 논리를 알려주는 스마트 힌트 숫자 퍼즐. 18개 언어, 일일 챌린지 및 듀얼 지원.',
      me2030Desc: '2030년 배경의 정치 전략 시뮬레이션. 8개 수도를 선택해 통치하고 내일 아침 신문 1면을 확인하세요.',
      mprDesc: '60 FPS 자전거 신문 배달 아케이드 게임. 7개 동네를 달리며 신문을 배달하세요.',
      baylightDesc: '한 손으로 즐기는 차분한 창고 정리 퍼즐.',
      casinoDesc: '전략 코치가 포함된 블랙잭, 텍사스 홀덤, 룰렛 (가상 칩 전용).',
      milaDesc: '어린이를 위한 영어 학습 앱 (100% 오프라인, 광고 없음, 구독 없음).',
      contactTitle: '문의 및 지원',
      contactSub: '플레이어 문의, 버그 제보 및 비즈니스 연락:',
      navAllGames: '전체 게임',
      navPrivacy: '개인정보 처리방침',
      navSupport: '고객 지원',
      smartHint: '스마트 힌트',
      restart: '↺ 다시 시작',
      openApp: '앱에서 열기',
      won: ' 퍼즐 완료!',
      statCoalition: '연정 지지율',
      statEconomy: '경제',
      statStability: '안정도',
      streak: '연속 정답',
      accuracy: '정확도',
      hands: '핸드',
      dealerUpcard: '딜러 카드',
      yourHand: '내 핸드',
      actHit: '히트 (Hit)',
      actStand: '스탠드 (Stand)',
      actDouble: '더블 (Double)',
      actSplit: '스플릿 (Split)'
    },
    'zh-TW': {
      heroTitle: 'aviisr-games',
      heroSub: '獨立手機遊戲工作室。為 iOS 與 Android 打造策略、益智與街機遊戲。',
      playablesTitle: '🎮 在瀏覽器中立即試玩',
      playablesSub: '無需安裝應用程式，直接在網頁上體驗互動試玩版與訓練器：',
      p1Desc: '透過智慧邏輯提示解開今日數獨。',
      p2Desc: '扮演總理帶領國家度過 3 個月的危機。',
      p3Desc: '掌握 21 點基本策略與數學機率。',
      playNow: '立即試玩',
      gamesTitle: '我們的遊戲',
      hubLink: '遊戲專頁',
      ninelyDesc: '提供逐步邏輯教學提示的極簡數字益智遊戲。支援 18 種語言、每日挑戰與好友對戰。',
      me2030Desc: '以 2030 年為背景的深度政治策略模擬。從 8 個首都中選擇並閱讀明日早報頭版。',
      mprDesc: '60 FPS 單車送報街機遊戲，穿梭於 7 個特色社區。',
      baylightDesc: '單手即可暢玩的療癒系倉庫分類益智遊戲。',
      casinoDesc: '內建策略教練的 21 點、德州撲克與輪盤（純虛擬籌碼）。',
      milaDesc: '兒童英語學習應用程式（100% 離線、零廣告、無訂閱）。',
      contactTitle: '聯絡與支援',
      contactSub: '玩家諮詢、問題回報或商務聯繫：',
      navAllGames: '所有遊戲',
      navPrivacy: '隱私權政策',
      navSupport: '支援',
      smartHint: '智慧提示',
      restart: '↺ 重新開始',
      openApp: '在應用程式中開啟',
      won: '完成挑戰！',
      statCoalition: '執政聯盟',
      statEconomy: '經濟',
      statStability: '穩定度'
    },
    'zh-CN': {
      heroTitle: 'aviisr-games',
      heroSub: '独立手游工作室。专为 iOS 和 Android 打造的策略、解谜与街机游戏。',
      playablesTitle: '🎮 在浏览器中畅玩',
      playablesSub: '无需安装应用，即可在网页中体验互动试玩与策略训练器：',
      p1Desc: '使用智能逻辑提示解开今日谜题。',
      p2Desc: '作为总理执政 3 个月并打印晨报头版。',
      p3Desc: '掌握 21 点基本策略与数学概率。',
      playNow: '立即开始',
      gamesTitle: '我们的游戏',
      hubLink: '游戏主页',
      ninelyDesc: '配备分步逻辑智能提示的极简数字解谜游戏。支持 18 种语言、每日挑战与好友对战。',
      me2030Desc: '2030 年政治策略模拟游戏。从 8 个首都中选择，阅读明日头条新闻。',
      mprDesc: '60 FPS 快节奏自行车送报街机游戏，穿越 7 个街区。',
      baylightDesc: '轻松解压的单手仓库分拣解谜游戏。',
      casinoDesc: '内置策略教练的 21 点、德州扑克与轮盘（纯虚拟筹码）。',
      milaDesc: '少儿英语学习应用（100% 离线、无广告、无订阅）。',
      contactTitle: '联系与支持',
      contactSub: '玩家咨询、错误反馈或商务合作：',
      navAllGames: '全部游戏',
      navPrivacy: '隐私政策',
      navSupport: '支持',
      smartHint: '智能提示',
      restart: '↺ 重新开始',
      openApp: '在应用中打开',
      won: '挑战完成！',
      streak: '连胜',
      accuracy: '准确率',
      hands: '局数',
      dealerUpcard: '庄家明牌',
      yourHand: '你的手牌',
      actHit: '要牌 (Hit)',
      actStand: '停牌 (Stand)',
      actDouble: '加倍 (Double)',
      actSplit: '分牌 (Split)'
    },
    'sv': {
      heroTitle: 'aviisr-games',
      heroSub: 'Oberoende mobilspelsstudio. Strategi-, pussel- och arkadspel för iOS och Android.',
      playablesTitle: '🎮 Spela i webbläsaren',
      playablesSub: 'Prova snabba spelbara webbdemos utan att installera en app:',
      p1Desc: 'Lös dagens pussel med smarta logiska ledtrådar.',
      p2Desc: 'Styr landet under 3 månader som premiärminister.',
      p3Desc: 'Bemästra grundläggande Blackjack-strategi.',
      playNow: 'Spela nu',
      gamesTitle: 'Våra Spel',
      hubLink: 'Spelsida',
      ninelyDesc: 'Minimalistiskt sifferpussel med smarta ledtrådar som lär ut logik steg för steg på 18 språk.',
      me2030Desc: 'Politisk strategisimulering år 2030. Välj bland 8 huvudstäder och läs morgondagens förstasida.',
      mprDesc: 'Snabbt 60 FPS arkadspel som tidningsbud på cykel genom 7 kvarter.',
      baylightDesc: 'Lugnt och tillfredsställande sorteringspussel med en tumme.',
      casinoDesc: 'Blackjack med strategicoach, Texas Hold’em och Roulette (endast virtuella marker).',
      milaDesc: 'Engelska för barn (100% offline, inga annonser, ingen prenumeration).',
      contactTitle: 'Kontakt & Support',
      contactSub: 'Spelarfrågor, felrapporter eller affärskontakt:',
      navAllGames: 'Alla spel',
      navPrivacy: 'Integritet',
      navSupport: 'Support',
      smartHint: 'Smart ledtråd',
      restart: '↺ Starta om',
      openApp: 'Öppna i appen',
      won: 'Löst!'
    },
    'da': {
      heroTitle: 'aviisr-games',
      heroSub: 'Uafhængigt mobilspilstudie. Strategi-, puslespil og arkadespil til iOS og Android.',
      playablesTitle: '🎮 Spil i din browser',
      playablesSub: 'Prøv interaktive webdemoer uden at installere en app:',
      p1Desc: 'Løs dagens puslespil med smarte logiske hints.',
      p2Desc: 'Reger i 3 måneder som premierminister.',
      p3Desc: 'Mestr grundlæggende Blackjack-strategi.',
      playNow: 'Spil nu',
      gamesTitle: 'Vores Spil',
      hubLink: 'Spilside',
      ninelyDesc: 'Minimalistisk talpuslespil med smarte hints, der lærer dig logik trin for trin på 18 sprog.',
      me2030Desc: 'Politisk strategisimulering i 2030. Vælg mellem 8 hovedstæder og læs morgendagens forside.',
      mprDesc: 'Hurtigt 60 FPS cykel-avisbud arkadespil gennem 7 kvarterer.',
      baylightDesc: 'Roligt sorteringspuslespil med én tommelfinger.',
      casinoDesc: 'Blackjack med strategisencoach, Texas Hold’em og Roulette (kun virtuelle jetoner).',
      milaDesc: 'Engelsk for børn (100% offline, ingen reklamer, intet abonnement).',
      contactTitle: 'Kontakt & Support',
      contactSub: 'Spillerhenvendelser, fejlrapporter eller forretningskontakt:',
      navAllGames: 'Alle spil',
      navPrivacy: 'Privatliv',
      navSupport: 'Support',
      smartHint: 'Smart hint',
      restart: '↺ Genstart',
      openApp: 'Åbn i app',
      won: 'Løst!'
    },
    'nb': {
      heroTitle: 'aviisr-games',
      heroSub: 'Uavhengig mobilspillstudio. Strategi-, pusle- og arkadespill for iOS og Android.',
      playablesTitle: '🎮 Spill i nettleseren',
      playablesSub: 'Prøv interaktive nettdemoer uten å installere en app:',
      p1Desc: 'Løs dagens oppgave med smarte logiske hint.',
      p2Desc: 'Styr landet i 3 måneder som statsminister.',
      p3Desc: 'Mestre grunnleggende Blackjack-strategi.',
      playNow: 'Spill nå',
      gamesTitle: 'Våre Spill',
      hubLink: 'Spillside',
      ninelyDesc: 'Minimalistisk tallpuslespill med smarte hint som lærer bort logikk trinn for trinn på 18 språk.',
      me2030Desc: 'Politisk strategisimulering i 2030. Velg blant 8 hovedsteder og les morgendagens forside.',
      mprDesc: 'Raskt 60 FPS arkadespill som avisbud på sykkel gjennom 7 nabolag.',
      baylightDesc: 'Rolig sorteringspuslespill med én tommel.',
      casinoDesc: 'Blackjack med strategitrener, Texas Hold’em og Roulette (kun virtuelle sjetonger).',
      milaDesc: 'Engelsk for barn (100% frakoblet, ingen reklame, ingen abonnement).',
      contactTitle: 'Kontakt og brukerstøtte',
      contactSub: 'Spillerhenvendelser, feilrapporter eller forretningskontakt:',
      navAllGames: 'Alle spill',
      navPrivacy: 'Personvern',
      navSupport: 'Brukerstøtte',
      smartHint: 'Smart hint',
      restart: '↺ Start på nytt',
      openApp: 'Åpne i appen',
      won: 'Løst!'
    },
    'fi': {
      heroTitle: 'aviisr-games',
      heroSub: 'Itsenäinen mobiilipelistudio. Strategia-, pulma- ja arcade-pelejä iOS- ja Android-laitteille.',
      playablesTitle: '🎮 Pelaa selaimessa',
      playablesSub: 'Kokeile pelattavia verkkodemoja asentamatta sovellusta:',
      p1Desc: 'Ratkaise päivän pulma älykkäillä logiikkavihjeillä.',
      p2Desc: 'Johda hallitusta 3 kuukauden ajan pääministerinä.',
      p3Desc: 'Opi Blackjackin optimaalinen perusstrategia.',
      playNow: 'Pelaa nyt',
      gamesTitle: 'Pelimme',
      hubLink: 'Pelisivu',
      ninelyDesc: 'Minimalistinen numeropulmapeli älykkäillä vaiheittaisilla vihjeillä 18 kielellä.',
      me2030Desc: 'Poliittinen strategiasimulaatio vuodelle 2030. Valitse 8 pääkaupungista ja lue huomisen etusivu.',
      mprDesc: 'Nopeatempoinen 60 FPS pyörälähetti-arcadepeli 7 naapurustossa.',
      baylightDesc: 'Rauhoittava yhden peukalon varastonlajittelupulma.',
      casinoDesc: 'Blackjack strategiavalmentajalla, Texas Hold’em ja Ruletti (vain virtuaalimerkkejä).',
      milaDesc: 'Englannin oppimispeli lapsille (100% offline, ei mainoksia, ei tilausta).',
      contactTitle: 'Yhteystiedot ja tuki',
      contactSub: 'Pelaajakysymykset, vikailmoitukset ja yritysyhteydenotot:',
      navAllGames: 'Kaikki pelit',
      navPrivacy: 'Tietosuoja',
      navSupport: 'Tuki',
      smartHint: 'Älyvihje',
      restart: '↺ Aloita alusta',
      openApp: 'Avaa sovelluksessa',
      won: 'Ratkaistu!'
    }
  };

  window.AVIISR_LANGS = AVIISR_LANGS;
  window.AVIISR_STRINGS = AVIISR_STRINGS;

  function resolveLanguage(supported, defaultLang) {
    // 1. URL query param: ?lang=xx
    try {
      var params = new URLSearchParams(window.location.search);
      var qLang = params.get('lang');
      if (qLang && supported.indexOf(qLang) !== -1) return qLang;
    } catch (e) {}

    // 2. URL hash: #en, #he, #ar, etc.
    var hash = (window.location.hash || '').replace(/^#/, '');
    if (hash && supported.indexOf(hash) !== -1) return hash;

    // 3. Stored choice
    try {
      var stored = localStorage.getItem('aviisr_lang');
      if (stored && supported.indexOf(stored) !== -1) return stored;
    } catch (e) {}

    // 4. Browser navigator language
    try {
      var nav = (navigator.language || navigator.userLanguage || '').toLowerCase();
      for (var i = 0; i < supported.length; i++) {
        var s = supported[i];
        if (s.toLowerCase() === nav) return s;
      }
      var baseNav = nav.split('-')[0];
      for (var j = 0; j < supported.length; j++) {
        var cand = supported[j];
        if (cand.split('-')[0].toLowerCase() === baseNav) return cand;
      }
    } catch (e) {}

    return defaultLang || 'en';
  }

  function applyLanguage(lang, options) {
    var supported = options.supported || ['en'];
    var translations = options.translations || {};
    var defaultLang = options.defaultLang || 'en';

    if (supported.indexOf(lang) === -1) lang = defaultLang;

    var meta = AVIISR_LANGS[lang] || { nativeName: lang, dir: 'ltr' };
    var dir = meta.dir || 'ltr';

    document.documentElement.lang = lang;
    document.documentElement.dir = dir;

    try {
      localStorage.setItem('aviisr_lang', lang);
    } catch (e) {}

    // Synchronize select dropdowns if present
    var selectElements = document.querySelectorAll('.lang-switcher, #lang-switcher');
    for (var i = 0; i < selectElements.length; i++) {
      selectElements[i].value = lang;
    }

    // Merge global strings + page-specific strings for active language and fallback
    var globalLangTable = AVIISR_STRINGS[lang] || {};
    var pageLangTable = translations[lang] || {};
    var globalFallback = AVIISR_STRINGS[defaultLang] || AVIISR_STRINGS['en'] || {};
    var pageFallback = translations[defaultLang] || translations['en'] || {};

    var i18nNodes = document.querySelectorAll('[data-i18n]');
    for (var k = 0; k < i18nNodes.length; k++) {
      var el = i18nNodes[k];
      var key = el.getAttribute('data-i18n');
      if (!key) continue;
      var val = pageLangTable[key] !== undefined ? pageLangTable[key]
        : (globalLangTable[key] !== undefined ? globalLangTable[key]
        : (pageFallback[key] !== undefined ? pageFallback[key] : globalFallback[key]));
      if (val !== undefined) {
        el.textContent = val;
      }
    }

    // Toggle multi-section visibility for pages using <section id="en">, <section id="he">, <section id="ar">
    var sections = document.querySelectorAll('section[id]');
    var langSectionIds = [];
    var hasExactMatch = false;
    for (var s = 0; s < sections.length; s++) {
      var sid = sections[s].getAttribute('id');
      if (AVIISR_LANGS[sid]) {
        langSectionIds.push(sections[s]);
        if (sid === lang) hasExactMatch = true;
      }
    }
    if (langSectionIds.length > 0) {
      var targetSectionId = hasExactMatch ? lang : (document.getElementById(defaultLang) ? defaultLang : 'en');
      for (var m = 0; m < langSectionIds.length; m++) {
        var sec = langSectionIds[m];
        var secId = sec.getAttribute('id');
        sec.style.display = (secId === targetSectionId) ? '' : 'none';
      }
    }

    // Notify custom listeners if any
    if (typeof options.onLanguageChange === 'function') {
      options.onLanguageChange(lang, meta);
    }
  }

  function renderSwitcher(container, options) {
    if (!container) return;
    var supported = options.supported || ['en'];
    var current = options.current || 'en';

    // Preserve any non-language navigation links (e.g. All Games, Privacy, Support)
    var preservedLinks = [];
    var existingAnchors = container.querySelectorAll('a');
    for (var a = 0; a < existingAnchors.length; a++) {
      var href = existingAnchors[a].getAttribute('href') || '';
      if (href.indexOf('#') !== 0) {
        preservedLinks.push(existingAnchors[a].cloneNode(true));
      }
    }

    var select = document.createElement('select');
    select.id = 'lang-switcher';
    select.className = 'lang-switcher';
    select.setAttribute('aria-label', 'Language');

    for (var i = 0; i < supported.length; i++) {
      var code = supported[i];
      var meta = AVIISR_LANGS[code] || { nativeName: code, englishName: code };
      var opt = document.createElement('option');
      opt.value = code;
      opt.textContent = meta.nativeName + (meta.englishName && meta.englishName !== meta.nativeName ? ' (' + meta.englishName + ')' : '');
      if (code === current) opt.selected = true;
      select.appendChild(opt);
    }

    select.addEventListener('change', function () {
      applyLanguage(this.value, options);
    });

    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    container.appendChild(select);

    for (var p = 0; p < preservedLinks.length; p++) {
      var sep = document.createTextNode(' · ');
      container.appendChild(sep);
      container.appendChild(preservedLinks[p]);
    }
  }

  window.AviisrI18n = {
    init: function (options) {
      options = options || {};
      var supported = options.supported || ['en'];
      var defaultLang = options.defaultLang || (supported.indexOf('he') !== -1 && supported[0] === 'he' ? 'he' : 'en');
      options.defaultLang = defaultLang;

      var currentLang = resolveLanguage(supported, defaultLang);
      options.current = currentLang;

      // Mount switcher if container exists
      var navContainer = document.querySelector('nav.lang') || document.querySelector('.lang-nav');
      if (navContainer) {
        renderSwitcher(navContainer, options);
      }

      applyLanguage(currentLang, options);

      // Listen to hashchange for anchor links (#en, #he, #ar)
      window.addEventListener('hashchange', function () {
        var h = (window.location.hash || '').replace(/^#/, '');
        if (h && supported.indexOf(h) !== -1) {
          applyLanguage(h, options);
        }
      });
    },
    setLanguage: function (lang, options) {
      applyLanguage(lang, options);
    }
  };
})();
