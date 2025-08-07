'use client';

import logo from '@/public/Logo.svg';
import home from '@/public/home-img.svg';
import Image from "next/image";
import Link from "next/link";
import { Button } from "./ui/button";

const Header = () => {
	return (
		<div className="flex flex-col items-center px-4 sm:px-8">
			{/* Header */}
			<div className="w-full flex justify-between items-center py-6">
				<Image
					src={logo}
					alt="logo recipes"
					className="w-[100px] max-[400px]:w-[80px]"
					priority
				/>
				<Link href="/recipes">
					<Button
						type="button"
						variant="link"
						className="bg-green-500 text-white px-12 py-5 rounded-full font-semibold text-base transition duration-300 hover:bg-primary hover:text-white max-[400px]:px-10"
					>
						Go To Recipes
					</Button>
				</Link>
			</div>
			<section className="flex justify-between items-center mt-24 w-full max-w-screen-xl max-[730px]:flex-col max-[730px]:text-center max-[730px]:mt-20">
				<div className="max-w-[370px] max-[730px]:max-w-full max-[730px]:mb-5 max-[730px]:px-5">
					<h1 className="text-[60px] font-serif leading-[50px] tracking-[3px] mb-8 text-primary max-[1000px]:text-[50px]">
						Easy and Smart Recipes
					</h1>
					<p className="text-[23px] leading-[40px] max-[1000px]:text-[18px]">
						Spend less time looking for the recipe you want. Here you will find
						diversity in recipes. No more repeating the same food every day. So,
						shall we cook?
					</p>
				</div>

				<Image
					src={home}
					alt="girl cooking"
					className="w-[480px] max-[1000px]:w-[400px] max-[400px]:w-[300px] mb-12"
					priority
				/>
			</section>
		</div>
	);
};

export default Header;
