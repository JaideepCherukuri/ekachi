import AnimObserver from "@/components/AnimObserver";
import Footer from "@/components/Footer";
import Hero from "@/components/Hero";
import HowItWorks from "@/components/HowItWorks";
import LogosBar from "@/components/LogosBar";
import MarqueeCTA from "@/components/MarqueeCTA";
import Navbar from "@/components/Navbar";
import WhatViktorDoes from "@/components/WhatViktorDoes";

export default function Home() {
	return (
		<main className="min-h-screen bg-[#faf9f6]">
			<AnimObserver />
			<Navbar />
			<Hero />
			<LogosBar />
			<HowItWorks />
			<WhatViktorDoes />
			<MarqueeCTA />
			<Footer />
		</main>
	);
}
