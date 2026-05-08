"use client";

import { useEffect, useState } from "react";

function EkachiLogo({ height = 28 }: { height?: number }) {
	return (
		<div className="flex items-center gap-2">
			<span
				style={{
					fontFamily: "var(--font-manrope,'Manrope',sans-serif)",
					fontWeight: 700,
					fontSize: height * 0.85,
					letterSpacing: "0.13em",
					color: "#111",
					lineHeight: 1,
				}}
			>
				EKACHI
			</span>
		</div>
	);
}

export { EkachiLogo };

export default function Navbar() {
	const [scrolled, setScrolled] = useState(false);

	useEffect(() => {
		const onScroll = () => setScrolled(window.scrollY > 10);
		window.addEventListener("scroll", onScroll, { passive: true });
		return () => window.removeEventListener("scroll", onScroll);
	}, []);

	return (
		<nav
			className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
			style={{
				background: scrolled ? "#fff" : "transparent",
				boxShadow: scrolled ? "0 1px 0 rgba(0,0,0,0.06)" : "none",
			}}
		>
			<div className="max-w-7xl mx-auto px-6 h-[60px] flex items-center justify-between">
				<EkachiLogo height={22} />
				<a
					href="https://app.ekachi.com"
					target="_blank"
					rel="noopener noreferrer"
					className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium hover:opacity-80 transition-opacity"
					style={{ background: "#111", color: "#fff" }}
				>
					Early Access
				</a>
			</div>
		</nav>
	);
}
