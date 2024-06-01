import { NextResponse } from 'next/server';

export async function POST(req) {
  try {
    // Parse the request body to get the external API URL and data
    const { url } = await req.json();

    // Make a request to the external API
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Parse the response from the external API
    const result = await response.json();

    // Return the result back to the client
    return NextResponse.json(result);
  } catch (error) {
    // Handle errors and return an error response
    return NextResponse.json({ error: 'Failed to fetch data' }, { status: 500 });
  }
}

export const config = {
  api: {
    bodyParser: true,
  },
};
