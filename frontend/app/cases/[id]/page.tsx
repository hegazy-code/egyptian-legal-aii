import ComingSoon from "@/components/ComingSoon";

// TODO(backend): needs auth + GET /cases/:id -- neither exists yet.
// params is awaited only so this reads correctly once real data is wired in.
export default async function CaseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <ComingSoon
      title={`القضية رقم ${id}`}
      note="تفاصيل القضية ستظهر هنا بعد ربط الخادم الخلفي ونظام الحسابات."
    />
  );
}


export function generateStaticParams() {
  return [{ id: "sample" }];
}
