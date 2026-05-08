import { EkachiLogo } from "@/components/Navbar";

export default function Footer() {
	return (
		<footer className="border-t border-[#E5E2DC] pt-16 pb-10 px-6">
			<div className="max-w-7xl mx-auto">
				<div className="mb-16">
					<div className="mb-4">
						<EkachiLogo height={20} />
					</div>
					<p className="text-[#A8A49E] text-sm leading-relaxed max-w-[280px]">
						The AI employee for any role.
					</p>
				</div>

				<div className="border-t border-[#E5E2DC] pt-6 text-[#C8C4BD] text-xs">
					© 2026 Ekachi. All rights reserved.
				</div>
			</div>
		</footer>
	);
}
