import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const formData = await req.formData();

  const file = formData.get("file") as File | null;
  const startPage = formData.get("start_page") as string;
  const endPage = formData.get("end_page") as string;
  const eudicCookie = formData.get("eudic_cookie") as string;

  if (!file) {
    return NextResponse.json({ error: "缺少 PDF 文件" }, { status: 400 });
  }
  if (!eudicCookie) {
    return NextResponse.json({ error: "缺少 Eudic Cookie" }, { status: 400 });
  }

  const lambdaUrl = process.env.LAMBDA_FUNCTION_URL;
  if (!lambdaUrl) {
    return NextResponse.json({ error: "LAMBDA_FUNCTION_URL 未配置" }, { status: 500 });
  }

  // Forward the file and params to Lambda Function URL
  const upstream = new FormData();
  upstream.append("file", file);
  upstream.append("start_page", startPage ?? "1");
  upstream.append("end_page", endPage ?? "15");
  upstream.append("eudic_cookie", eudicCookie);

  const lambdaRes = await fetch(lambdaUrl, {
    method: "POST",
    body: upstream,
  });

  if (!lambdaRes.ok) {
    const text = await lambdaRes.text();
    return NextResponse.json(
      { error: `Lambda 返回错误: ${lambdaRes.status} ${text}` },
      { status: 502 }
    );
  }

  const data = await lambdaRes.json();
  return NextResponse.json(data);
}
