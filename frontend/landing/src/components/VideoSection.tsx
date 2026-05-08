import Image from "next/image";

export default function VideoSection() {
	return (
		<section className="py-20 px-6 border-t border-[#E5E2DC]">
			<div className="max-w-4xl mx-auto">
				<div
					className="relative w-full rounded-2xl overflow-hidden border border-[#E5E2DC]"
					style={{ aspectRatio: "16/9" }}
				>
					<Image
						src="/images/launch-cover.jpg"
						alt="Ekachi launch cover"
						fill
						style={{ objectFit: "cover" }}
						priority
					/>
				</div>
			</div>
		</section>
	);
}
