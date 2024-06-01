"use client";

import axios from "axios";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { z } from "zod";
import { useRef, useState } from "react";

const formSchema = z.object({
    topicname: z.string().min(2),
});

export default function FrontPage() {
    const [isFocused, setIsFocused] = useState(false);
    const [result, setResult] = useState<string>('');
    const textAreaRef = useRef<HTMLTextAreaElement>(null);

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            topicname: '',
        },
    });

    const onSubmit = async (values: z.infer<typeof formSchema>) => {
        try {
            const response = await fetch('/api/proxy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: `http://127.0.0.1:5000/get_summ?topic=${values.topicname}` }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            const summary = data.summary;

            if (textAreaRef.current) {
                textAreaRef.current.value = summary;
            }

            setResult(summary);
            console.log(summary);
        } catch (error) {
            console.error('Error fetching summary:', error);
            setResult('Error fetching summary');
            if (textAreaRef.current) {
                textAreaRef.current.value = 'Error fetching summary';
            }
        }
    };

    const handleFocus = () => {
        setIsFocused(true);
    };

    const handleBlur = (value: string) => {
        if (value === "") {
            setIsFocused(false);
        }
    };

    return (
        <div className="flex flex-col h-full w-full">
            <h1 className="text-6xl bg-slate-800 border border-slate-600 py-2 rounded-xl text-stone-300 w-full text-center font-bold">News Summarization</h1>
            <div className="flex border-2 border-slate-700 p-6 rounded-xl flex-col mt-10 gap-8 justify-center items-center">
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="flex relative   w-full gap-x-4 justify-center items-center">
                        <FormField
                            control={form.control}
                            name="topicname"
                            render={({ field }) => (
                                <FormItem className="flex w-full">
                                    <FormLabel
                                        htmlFor="text"
                                        className={`absolute text-sm top-3 left-2 transition-all duration-300 ${
                                            isFocused || field.value ? 'top-[-22px] text-xl' : ''
                                        }`}
                                    >
                                        Topic Name
                                    </FormLabel>
                                    <FormControl>
                                        <Input
                                            onFocus={handleFocus}
                                           
                                            placeholder=""
                                            {...field}
                                            className="rounded-xl bg-slate-800 border-[0] focus:border-2 focus:border-slate-600"
                                        />
                                    </FormControl>
                                </FormItem>
                            )}
                        />
                        <button type="submit" className=" mt-2 bg-gradient-to-tr from-slate-800 to-slate-600 text-stone-300 text-black px-6 py-2 rounded-xl text-sm">
                            Submit
                        </button>
                    </form>
                </Form>
                <div className="flex flex-col w-full gap-4 text-center">
                    <Label htmlFor="text" className="text-4xl">
                        Summary
                    </Label>
                    <textarea ref={textAreaRef} value={result} disabled className="p-4 rounded-xl h-40 text-white bg-slate-800" />
                </div>
            </div>
        </div>
    );
}
