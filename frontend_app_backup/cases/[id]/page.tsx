import ComingSoon from "@/components/ComingSoon";

// TODO(backend): needs auth + GET /cases/:id -- neither exists yet.
// params is awaited only so this reads correctly once real data is wired in.
export default async function CaseDetailPage(props: PageProps<"/cases/[id]">) {
  const { id } = await props.params;
  return (
    <ComingSoon
      title={`القضية رقم ${id}`}
      note="تفاصيل القضية ستظهر هنا بعد ربط الخادم الخلفي ونظام الحسابات."
    />
  );
}
