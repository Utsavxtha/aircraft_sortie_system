(use-modules (guix packages)
             (guix download)
             (guix build-system python)
             (guix licenses)
             (gnu packages python)
             (gnu packages python-xyz)
             (gnu packages tcl))

;; ── darkdetect (required by customtkinter) ───────────────────────────────────
(define python-darkdetect
  (package
    (name "python-darkdetect")
    (version "0.8.0")
    (source (origin
              (method url-fetch)
              (uri (pypi-uri "darkdetect" version))
              (sha256
               (base32
                "REPLACE_WITH_REAL_HASH"))))
    (build-system python-build-system)
    (home-page "https://github.com/albertosottile/darkdetect")
    (synopsis "Detect OS dark/light mode from Python")
    (description "Detect if the OS is using dark mode.")
    (license license:bsd-3)))

;; ── customtkinter ────────────────────────────────────────────────────────────
(define python-customtkinter
  (package
    (name "python-customtkinter")
    (version "5.2.2")
    (source (origin
              (method url-fetch)
              (uri (pypi-uri "customtkinter" version))
              (sha256
               (base32
                "REPLACE_WITH_REAL_HASH"))))
    (build-system python-build-system)
    (propagated-inputs
     (list python-darkdetect tk))
    (home-page "https://github.com/TomSchimansky/CustomTkinter")
    (synopsis "Modern and customizable Tkinter UI library")
    (description "A modern Python UI library based on Tkinter.")
    (license license:expat)))

;; ── Final manifest ───────────────────────────────────────────────────────────
(packages->manifest
 (list
  python            ;; Python 3 runtime (includes sqlite3)
  python-sqlalchemy ;; ORM — available in gnu packages python-xyz
  python-customtkinter ;; GUI (defined above)
  tk))              ;; Tcl/Tk backend for 