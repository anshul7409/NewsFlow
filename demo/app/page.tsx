import FrontPage from "@/components/Frontpage";
import Image from "next/image";
import { Montserrat } from 'next/font/google';

const montserrat = Montserrat({
  weight: ['300', '400', '500', '700'],
  subsets: ['latin'],
  display:'swap',
  fallback: ['Arial', 'sans-serif'],
});


export default function Home() {
  return (
    <main   className="flex flex-col items-center justify-between mt-10 mx-10">
        <div className={`${montserrat.className} flex min-h-dvh w-full`}>
            <FrontPage/>
        </div>
    </main>
  );
}
